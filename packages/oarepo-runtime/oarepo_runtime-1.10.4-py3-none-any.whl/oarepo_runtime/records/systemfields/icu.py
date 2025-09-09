from abc import abstractmethod, abstractproperty
from functools import cached_property
from typing import Dict

from flask import current_app
from invenio_records.systemfields import SystemField

from oarepo_runtime.records.relations.lookup import lookup_key
from oarepo_runtime.records.systemfields.mapping import MappingSystemFieldMixin


class ICUBase(MappingSystemFieldMixin, SystemField):
    """
    Base class for ICU system fields.
    It provides the basic functionality for ICU fields, such as
    getting the attribute name and handling the key.
    """

    def __init__(self, source_field=None, key=None):
        super().__init__(key=key)
        self._attr_name = key or self.__class__.__name__.lower()
        self.source_field = source_field

    @cached_property
    def languages(self) -> Dict[str, Dict]:
        icu_languages = current_app.config.get("OAREPO_ICU_LANGUAGES", {})
        if icu_languages:
            return icu_languages

        primary_language = current_app.config.get("BABEL_DEFAULT_LOCALE", "en")
        # list of tuples [lang, title], just take lang
        babel_languages = [x[0] for x in current_app.config.get("I18N_LANGUAGES", [])]

        return {primary_language: {}, **{k: {} for k in babel_languages}}

    def get_values(self, data, language):
        ret = []
        for l in lookup_key(data, f"{self.source_field}"):
            if isinstance(l.value, str):
                # take single value as being always the the language provided
                ret.append(l.value)
            elif isinstance(l.value, dict):
                # expected to be {"cs": "", "en": ""}
                val = l.value.get(language)
                if val:
                    ret.append(val)
                elif "lang" in l.value:
                    # for [{"lang": "", "value": ""}, ...] we get each item separately
                    # that's why we do not iterate over l.value
                    if l.value["lang"] == language:
                        ret.append(l.value["value"])
        return ret

    @abstractproperty
    def mapping(self):
        """
        The mapping for the field. It should return a dictionary with the
        mapping for the field, based on the current configuration of the application.
        """
        raise NotImplementedError("Subclasses must implement the mapping property.")

    @abstractmethod
    def search_dump(self, data, record):
        """
        Dump custom field. This method should be implemented by subclasses
        to provide the functionality for dumping the field data into the
        OpenSearch data structure.
        """
        raise NotImplementedError("Subclasses must implement the search_dump method.")

    def search_load(self, data, record_cls):
        """
        Just remove the field from the data on load.
        """
        data.pop(self.attr_name, None)

    def __get__(self, instance, owner):
        return self


class ICUField(ICUBase):
    """
    A system field that acts as an opensearch "proxy" to another field.
    It creates a top-level mapping field with the same name and copies
    content of {another field}.language into {mapping field}.language.

    The language accessor can be modified by overriding get_values method.
    """

    def __init__(self, *, source_field, key=None):
        super().__init__(source_field=source_field, key=key)

    def search_dump(self, data, record):
        ret = {}
        for lang in self.languages:
            r = self.get_values(data, lang)
            if r:
                # if the language is not empty, add it to the result
                # otherwise do not add it at all to safe transport
                ret[lang] = r
        if ret:
            data[self.attr_name] = ret


class ICUSortField(ICUField):
    """
    A field that adds icu sorting field
    """

    def __init__(self, *, source_field, key=None):
        super().__init__(source_field=source_field, key=key)

    @property
    def mapping(self):
        return {
            self.attr_name: {
                "type": "object",
                "properties": {
                    lang: {
                        "type": "icu_collation_keyword",
                        "index": False,
                        "language": lang,
                        **setting.get("collation", {}),
                    }
                    for lang, setting in self.languages.items()
                },
            },
        }


class ICUSuggestField(ICUField):
    """
    A field that adds icu-aware suggestion field
    """

    def __init__(self, source_field, key=None):
        super().__init__(source_field=source_field, key=key)

    @property
    def mapping(self):
        return {
            self.attr_name: {
                "type": "object",
                "properties": {
                    lang: setting.get(
                        "suggest",
                        {
                            "type": "text",
                            "fields": {
                                "original": {
                                    "type": "search_as_you_type",
                                },
                                "no_accent": {
                                    "type": "search_as_you_type",
                                    "analyzer": "accent_removal_analyzer",
                                },
                            },
                        },
                    )
                    for lang, setting in self.languages.items()
                },
            },
        }

    @property
    def mapping_settings(self):
        return {
            "analysis": {
                "analyzer": {
                    "accent_removal_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            }
        }


class ICUSearchAnalyzerMixin:

    default_stemming_analyzers = {
        "stemming_analyzer_cs": {
            "tokenizer": "standard",
            "filter": ["stemming_filter_cs", "lowercase"],
        },
        "stemming_analyzer_en": {
            "tokenizer": "standard",
            "filter": ["stemming_filter_en", "lowercase"],
        },
        "ascii_folding_analyzer": {
            "tokenizer": "standard",
            "filter": ["ascii_folding_filter", "lowercase"],
        },
        "lowercase_analyzer": {
            "tokenizer": "standard",
            "filter": ["lowercase"],
        },
    }

    default_stemming_filters = {
        "stemming_filter_cs": {
            "type": "stemmer",
            "name": "czech",
            "language": "czech",
        },
        "stemming_filter_en": {
            "type": "stemmer",
            "name": "english",
            "language": "english",
        },
        "ascii_folding_filter": {"type": "asciifolding", "preserve_original": True},
    }

    @property
    def mapping_settings(self):
        return {
            "analysis": {
                "analyzer": current_app.config.get(
                    "OAREPO_ICU_SEARCH_ANALYZERS", self.default_stemming_analyzers
                ),
                "filter": current_app.config.get(
                    "OAREPO_ICU_SEARCH_FILTERS", self.default_stemming_filters
                ),
            }
        }


class ICUSearchField(ICUSearchAnalyzerMixin, ICUField):
    """
    A field that adds stemming-aware search field for multilingual data (
        e.g. data that contains {"cs": "...", "en": "..."}
        or [{"lang": "cs", "value": "..."}, ...]
    )
    """

    def __init__(self, source_field, key=None, boost=1):
        super().__init__(source_field=source_field, key=key)
        self.boost = boost

    @property
    def mapping(self):
        return {
            self.attr_name: {
                "type": "object",
                "properties": {
                    # normal stemming
                    lang: setting.get(
                        "search",
                        {
                            "type": "text",
                            "boost": 1 * self.boost,
                            "fields": {
                                "stemmed": {
                                    "type": "text",
                                    "analyzer": f"stemming_analyzer_{lang}",
                                    "boost": 0.5 * self.boost,
                                },
                                "lowercase": {
                                    "type": "text",
                                    "boost": 0.8 * self.boost,
                                    "analyzer": "lowercase_analyzer",
                                },
                                "ascii_folded": {
                                    "type": "text",
                                    "analyzer": "ascii_folding_analyzer",
                                    "boost": 0.3 * self.boost,
                                },
                            },
                        },
                    )
                    for lang, setting in self.languages.items()
                },
            },
        }

    def get_values(self, data, language):
        return super().get_values(data, language=language)


class SingleLanguageSearchField(ICUSearchAnalyzerMixin, ICUBase):
    """
    A base class for single-language search fields - that is, data contain a text
    value in a pre-defined, single language.
    """

    def __init__(self, *, source_field, key=None, language=None, boost=1):
        super().__init__(source_field=source_field, key=key)
        self.language = language
        self.boost = boost

    def search_dump(self, data, record):
        """Dump custom field."""
        ret = self.get_values(data, language=self.language)
        if ret:
            data[self.attr_name] = ret


class FulltextIndexField(SingleLanguageSearchField):
    """
    A system field that makes the field searchable in OpenSearch,
    regardless if it is indexed/analyzed, embedded in Nested or not.

    It creates a top-level mapping field and copies
    content of {source_field} into it. It also provides the correct mapping
    for the field based on the current configuration of the application.

    Unlike the ICU, this field is a single-language and the language should
    be provided when initializing the field.
    It defaults to the BABEL_DEFAULT_LOCALE if not provided.
    """

    @property
    def mapping(self):
        language = self.language or current_app.config.get("BABEL_DEFAULT_LOCALE", "en")
        mapping_settings = self.languages.get(language, None)
        if mapping_settings:
            mapping_settings = mapping_settings.get("search")
        if not mapping_settings:
            mapping_settings = {
                "type": "text",
                "boost": 1 * self.boost,
                "fields": {
                    "stemmed": {
                        "type": "text",
                        "analyzer": f"stemming_analyzer_{language}",
                        "boost": 0.5 * self.boost,
                    },
                    "lowercase": {
                        "type": "text",
                        "boost": 0.8 * self.boost,
                        "analyzer": "lowercase_analyzer",
                    },
                    "ascii_folded": {
                        "type": "text",
                        "analyzer": "ascii_folding_analyzer",
                        "boost": 0.3 * self.boost,
                    },
                },
            }

        return {self.attr_name: mapping_settings}

    def search_load(self, data, record_cls):
        """Load custom field."""
        data.pop(self.attr_name, None)


class TermIndexField(SingleLanguageSearchField):
    """
    A system field that makes the field searchable in OpenSearch,
    regardless if it is indexed/analyzed, embedded in Nested or not.

    It creates a top-level mapping field and copies
    content of {source_field} into it. It also provides the correct mapping
    for the field based on the current configuration of the application.

    Unlike the ICU, this field is a single-language and the language should
    be provided when initializing the field.
    It defaults to the BABEL_DEFAULT_LOCALE if not provided.
    """

    @property
    def mapping(self):
        mapping_settings = {
            "type": "keyword",
            "boost": 1 * self.boost,
            "ignore_above": 256,
        }

        return {self.attr_name: mapping_settings}
