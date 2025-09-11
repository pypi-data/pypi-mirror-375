import logging
from abc import ABCMeta, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from typing import Generic, Iterable, Iterator, NamedTuple, Sequence, TypeVar

import torch
from tdm import TalismanDocument, not_filter
from tdm.abstract.datamodel import FactStatus
from tdm.datamodel.facts import AtomValueFact, MentionFact
from tdm.datamodel.mentions import TextNodeMention
from tdm.datamodel.nodes import TextNodeMetadata
from tdm.datamodel.values import StringValue
from typing_extensions import Self

from tie_ml_base.huggingface_pipeline.normalization_wrapper.config import StringNormalizerConfig
from tie_ml_base.torch_wrapper import TorchModule
from tp_interfaces.abstract import AbstractConfigConstructableModel, AbstractDocumentProcessor
from tp_interfaces.domain.abstract import AbstractLiteralValueType
from tp_interfaces.domain.manager import DomainManager

logger = logging.getLogger(__name__)


@dataclass
class TextMentionData:
    language: str
    related_facts: list[AtomValueFact]
    text: str


_MentionData = NamedTuple('_MentionData', (('lang', str), ('text', str)))

_TextMentionData = TypeVar('_TextMentionData', bound=TextMentionData)
_Config = TypeVar('_Config', bound=StringNormalizerConfig)


class AbstractMlStringNormalizer(
    TorchModule,
    AbstractConfigConstructableModel,
    AbstractDocumentProcessor[_Config],
    Generic[_Config, _TextMentionData],
    metaclass=ABCMeta
):
    def __init__(self, model_languages: Iterable[str], preferred_device: str | torch.device = None):
        super().__init__(preferred_device=preferred_device)
        self._model_languages = tuple(model_languages)
        self._str_atom_types: set[str] | None = None

    async def __aenter__(self) -> Self:
        async with DomainManager() as manager:
            domain = await manager.domain

        self._str_atom_types = {t.id for t in domain.get_types(AbstractLiteralValueType) if t.value_type is StringValue}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._str_atom_types = None

    async def process_doc(self, document: TalismanDocument, config: StringNormalizerConfig) -> TalismanDocument:
        def _filter(atom: AtomValueFact) -> bool:
            if atom.str_type_id not in self._str_atom_types:
                return False
            return config.check_type(atom, document)

        facts = document.get_facts(
            type_=AtomValueFact,
            filter_=(not_filter(AtomValueFact.status_filter([FactStatus.APPROVED, FactStatus.DECLINED])),
                     AtomValueFact.empty_value_filter(), _filter)
        )
        return document.with_facts(await self.normalize_facts(list(facts), document, config))

    def _get_mention_data(self, mention_fact: MentionFact, config: StringNormalizerConfig) -> _MentionData | None:
        if not isinstance(mention_fact.mention, TextNodeMention):
            return None

        mention: TextNodeMention = mention_fact.mention
        node_language = mention.node.metadata.language or TextNodeMetadata.UNKNOWN_LANG
        lang = config.get_lang(node_language, self._model_languages)
        if lang not in self._model_languages:
            logger.warning(f'Ignore mention <{mention_fact.id}> because unsupported language <{lang}>. '
                           f'Supported languages: {", ".join(self._model_languages)}')
            return None

        mention_len = mention.end - mention.start
        if not config.check_length(mention_len):
            logger.warning(f'Ignore mention <{mention_fact.id}> because length of mention <{mention_len}> more than max length <'
                           f'{config.max_token_length}>.')
            return None
        text = mention.node.content[mention.start: mention.end]
        return _MentionData(lang=lang, text=text)

    @abstractmethod
    def _convert_to_mention_data(self, lang: str, facts: list[AtomValueFact], text: str) -> _TextMentionData:
        pass

    def _collect_mention_data(self, mentions: Iterator[MentionFact], config: _Config) -> Sequence[_TextMentionData]:
        res: dict[_MentionData, list[AtomValueFact]] = defaultdict(list)

        for mention in mentions:
            lang_text = self._get_mention_data(mention, config)
            if lang_text:
                res[lang_text].append(mention.value)

        return [self._convert_to_mention_data(data.lang, values, data.text) for data, values in res.items()]

    async def normalize_facts(self, facts: Iterable[AtomValueFact], doc: TalismanDocument, config: _Config)\
            -> Iterable[AtomValueFact]:
        possible_mentions = (m for atom in facts for m in doc.related_facts(atom, type_=MentionFact))
        mentions = self._collect_mention_data(possible_mentions, config)
        normalized_mentions = self._normalize_mentions(mentions)

        fact_values = defaultdict(list)
        for normalized_mention in normalized_mentions:
            for fact in normalized_mention.related_facts:
                fact_values[fact].extend(self._convert(normalized_mention.text))

        return [replace(fact, value=tuple(self._set_confidence(fact_values[fact]))) if fact in fact_values else fact for fact in facts]

    async def normalize_fact(self, fact: AtomValueFact, doc: TalismanDocument, config: _Config) -> AtomValueFact:
        res = tuple(await self.normalize_facts([fact], doc, config))
        return res[0] if len(res) else fact

    @abstractmethod
    def _normalize_mentions(self, mentions: Sequence[_TextMentionData]) -> Sequence[_TextMentionData]:
        pass

    @staticmethod
    def _convert(value: str) -> Iterator[StringValue]:
        try:
            yield StringValue(value=value)
        except ValueError:
            logger.warning(f'ValueError occurred during conversion of "{value}".')

    @staticmethod
    def _set_confidence(normalized_mentions: Iterable[StringValue]) -> Iterator[StringValue]:
        """
        Counts the confidence for each normalized value and sorts the values by confidence.
        """
        c = Counter(normalized_mentions)
        for value, value_count in c.most_common():
            yield replace(value, confidence=value_count / c.total())
