from abc import ABCMeta, abstractmethod
from typing import Annotated

from pydantic import ConfigDict, Field, PrivateAttr, WithJsonSchema
from tdm import TalismanDocument
from tdm.abstract.datamodel import AbstractLinkFact
from tdm.datamodel.facts import AtomValueFact

from tp_interfaces.abstract import ImmutableBaseModel


class AbstractLanguageStrategy(ImmutableBaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_lang(self, lang: str, supported_langs: tuple[str, ...]) -> str | None:
        raise NotImplementedError


class BaseLanguageStrategy(AbstractLanguageStrategy):
    """Use node language"""
    model_config = ConfigDict(title="Без настроек", json_schema_extra={'description': 'Используется язык ноды'})

    def get_lang(self, lang: str, supported_langs: tuple[str, ...]) -> str | None:
        return lang


class ForceOneLang(AbstractLanguageStrategy):
    """
    Force language 'lang'
    if 'for_all=true' than ignore node language else use force lang only for unsupported languages
    """
    lang: str = Field(title="Язык")
    for_all: bool = Field(False, title="Для всех значений")
    model_config = ConfigDict(title="Задать язык", json_schema_extra={'description': 'Принудительно задаёт язык'})

    def get_lang(self, lang: str, supported_langs: tuple[str, ...]) -> str | None:
        if self.for_all:
            return self.lang

        return lang if lang in supported_langs else self.lang


class LangMappingStrategy(AbstractLanguageStrategy):
    """
    map supported language(including unknown) to list of unsupported language
    """
    lang_mapping: dict[str, tuple[str, ...]]
    _lang_mapping: dict[str, str] = PrivateAttr()  # mapping unsupported language to supported
    model_config = ConfigDict(extra='allow', title="Отображение языков", json_schema_extra={
        'description': 'Задаёт отображение поддерживаемого языка в список неподдерживаемых'
    })

    def model_post_init(self, context):
        real_mapping = {value: key for key, values in self.lang_mapping.items() for value in values}
        self._lang_mapping = real_mapping

    def get_lang(self, lang: str, supported_langs: tuple[str, ...]) -> str:
        return self._lang_mapping.get(lang, lang)

    def __hash__(self):
        return hash(tuple(self.lang_mapping.items()))


_TypeStr = Annotated[str, WithJsonSchema({"type": "string", "title": "Тип предметной области"})]


class StringNormalizerConfig(ImmutableBaseModel):
    possible_types: tuple[_TypeStr, ...] = Field(
        tuple(),
        title="Используемые типы характеристик и значений характеристик из предметной области"
    )
    excluded_types: tuple[_TypeStr, ...] = Field(
        tuple(),
        title="Типы характеристик и значений характеристик из предметной области, которые будут исключены из обработки"
    )
    lang_strategy: BaseLanguageStrategy | ForceOneLang | LangMappingStrategy = Field(BaseLanguageStrategy(), title="Стратегия обработки")
    max_token_length: int = Field(
        150,
        title="Максимальная длина текста для обработки",
        description="Для отмены лимита задайте в поле значение `-1`"
    )

    _max_token_length: int | None = PrivateAttr()
    _excluded_set: set[str] = PrivateAttr()
    _possible_set: set[str] = PrivateAttr()

    model_config = ConfigDict(title="Настройка ml-обработчика строк")

    def model_post_init(self, __context) -> None:
        self._excluded_set = set(self.excluded_types)
        self._possible_set = set(self.possible_types)
        self._max_token_length = None if self.max_token_length < 0 else self.max_token_length

    def check_type(self, atom: AtomValueFact, document: TalismanDocument) -> bool:
        if not self._excluded_set and not self._possible_set:
            return True
        type_id = atom.str_type_id
        if type_id in self._excluded_set:
            return False

        related_type_ids = {prop.type_id.id for prop in document.related_facts(atom, AbstractLinkFact)}

        if self._excluded_set & related_type_ids:
            return False

        if not self._possible_set:
            return True

        return type_id in self._possible_set or bool(self._possible_set & related_type_ids)

    def check_length(self, length: int) -> bool:
        return self._max_token_length is None or length <= self._max_token_length

    def get_lang(self, lang: str, supported_langs: tuple[str, ...]):
        return self.lang_strategy.get_lang(lang, supported_langs)


if __name__ == "__main__":
    import json
    print(json.dumps(StringNormalizerConfig.model_json_schema(), indent=2, ensure_ascii=False))
