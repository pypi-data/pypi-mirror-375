import logging
from dataclasses import replace
from typing import Any, Iterable, Sequence, Type

import torch
from tdm.datamodel.facts import AtomValueFact
from transformers import pipeline
from typing_extensions import Self

from tie_ml_base.env import get_cpu_batch_size, get_gpu_batch_size
from tie_ml_base.huggingface_pipeline.normalization_wrapper.abstract import AbstractMlStringNormalizer, TextMentionData
from tie_ml_base.huggingface_pipeline.normalization_wrapper.config import StringNormalizerConfig
from tie_ml_base.tools.memory_management import cuda_handler

logger = logging.getLogger(__name__)


class _Text2TextMentionData(TextMentionData):
    @property
    def get_request(self) -> str:
        return f">>{self.language}<< {self.text}"


class Text2TextNormalizer(
    AbstractMlStringNormalizer[StringNormalizerConfig, _Text2TextMentionData]
):
    """
    A hugging face pipeline wrapper for AtomValueFact's StringValue normalization using text2text model,
    for some supported languages.
    """
    def __init__(self, normalizer_pipeline: pipeline, model_languages: Iterable[str], preferred_device: str | torch.device = None):
        super().__init__(model_languages, preferred_device=preferred_device)
        self._pipeline = normalizer_pipeline
        self._model = self._pipeline.model
        self._tokenizer = self._pipeline.tokenizer
        self._cpu_batch_size = get_cpu_batch_size()
        self._gpu_batch_size = get_gpu_batch_size()
        self._possible_type_ids: set[str] | None = None

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    @cuda_handler
    def _normalize_mentions(self, mentions: Sequence[_Text2TextMentionData]) -> Sequence[_Text2TextMentionData]:
        if not mentions:
            return []
        # Normalization part
        self._pipeline.device = self.device
        batch_size = self._cpu_batch_size if self.device == torch.device('cpu') else self._gpu_batch_size
        to_be_normalized = [mention.get_request for mention in mentions]
        # Setting the maximum output tokens' number to (1.5 * maximum input tokens' number) to prevent value cutting.
        max_output_tokens = int(1.5 * len(max(map(self._tokenizer.encode, to_be_normalized), key=len)))
        try:
            results = self._pipeline(to_be_normalized, clean_up_tokenization_spaces=True, num_beams=5,
                                     batch_size=batch_size, max_new_tokens=max_output_tokens)
            logger.info(f'Normalize mentions: {to_be_normalized}')
        except ValueError:
            logger.warning(f'ValueError occurred during normalization of mentions: {", ".join([m.text for m in mentions])}.')
            return []

        return [replace(mention, text=result['generated_text']) for mention, result in zip(mentions, results)]

    def _convert_to_mention_data(self, lang: str, facts: list[AtomValueFact], text: str) -> _Text2TextMentionData:
        return _Text2TextMentionData(language=lang, related_facts=facts, text=text)

    def forward(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls.from_model_name(**config)

    @classmethod
    def from_model_name(cls, model_name_or_path: str, model_languages: Iterable[str], preferred_device: str | torch.device = None) -> Self:
        pl = pipeline(
            model=model_name_or_path,
            tokenizer=model_name_or_path,
            task='text2text-generation',
            framework='pt',
            device=torch.device('cpu')
        )
        return cls(pl, model_languages, preferred_device)

    @property
    def config_type(self) -> Type[StringNormalizerConfig]:
        return StringNormalizerConfig
