import os
import re
import enum
import polars as pl
from typing import Optional, Union, Iterable
from datetime import datetime

from pydantic import BaseModel, PrivateAttr
from flashtext2 import KeywordProcessor

PATTERNS = {
    r"[12][0-9]{2}(0[1-9]|1[0-2])(2[AB]|[0-9]{2})[0-9]{3}[0-9]{3}([0-9]{2})": "<NIR>",
    r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b": "<EMAIL>",
    # r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}": "<PHONE>",
    r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>"
}
NATURAL_PLACEHOLDERS = {
    '<PER>': 'Margaret Hamilton',
    '<NAME>': 'Margaret Hamilton',
    '<CODE_POSTAL>': '42000',
    '<DATE>': '1970/01/01',
    '<IPP>': 'IPPPH:0987654321',
    '<NIR>': '012345678987654',
    '<EMAIL>': 'place.holder@anonymization.cdc',
    '<PHONE>': '0611223344',
}
PLACEHOLDER_REGEX = re.compile(r'<[A-Z_]+>')


class PersonalInfo(BaseModel):

    first_name: str
    last_name: str
    birth_name: Optional[str]
    birthdate: datetime
    ipp: str
    postal_code: Optional[str]

    @staticmethod
    def from_dict(d: dict):
        return PersonalInfo(
            first_name=d.get('PRENOM_PATIENT') or '',
            last_name=d.get('NOM_USUEL_PATIENT') or '',
            birth_name=d.get('NOM_NAISSANCE') or '',
            birthdate=d.get('DATE_NAIS') or datetime(
                year=1000, month=1, day=1),
            postal_code=d.get('CODE_POSTAL', '0'),
            ipp=d.get('IPP_PATIENT') or '',
        )


class AnonymizationMethods(enum.Enum):
    dummy = enum.auto()
    straight = enum.auto()
    sneaky = enum.auto()
    confident_snake = enum.auto()

    @staticmethod
    def default() -> AnonymizationMethods:
        assert isinstance(AnonymizationMethods.straight.name, str), type(
            AnonymizationMethods.straight.name)
        return AnonymizationMethods.dummy


AnonymizationMethodsClass = AnonymizationMethods


class Anonymizer(ConfigurableResource):

    _tokenizer = PrivateAttr()
    _model = PrivateAttr()
    _nlp = PrivateAttr()
    _context = PrivateAttr()

    @staticmethod  # shortcut for client
    def AnonymizationMethods():
        return AnonymizationMethodsClass

    # def setup_for_execution(self, context=None):
    #     "Load model from local installation, or from remote if not found"
    #     self._context = context
    #     self._nlp = None

    # def _init_ner(self):
    #     from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    #     model_name = os.getenv(
    #         'ANONYMIZER_MODEL', 'Jean-Baptiste/camembert-ner-with-dates')
    #     local_models_dir = os.getenv('ANONYMIZER_MODELS_PATH', 'models/')
    #     local_path = os.path.join(local_models_dir, model_name)
    #     context = self._context
    #     if os.path.exists(local_path):
    #         if context:
    #             context.log.info(f"Loading model {local_path}")
    #         model = AutoModelForTokenClassification.from_pretrained(local_path)
    #         tokenizer = AutoTokenizer.from_pretrained(local_path)
    #     else:  # model was not downloaded before ; do it !
    #         if context:
    #             context.log.info(
    #                 f"Model {model_name} was not found locally at {local_path}. Downloading…")
    #         model = AutoModelForTokenClassification.from_pretrained(model_name)
    #         tokenizer = AutoTokenizer.from_pretrained(model_name)
    #         # save them for later use
    #         model.save_pretrained(local_path)
    #         tokenizer.save_pretrained(local_path)

    #     if context:
    #         context.log.info("Model and tokenizers loaded")

    #     self._nlp = pipeline(
    #         'ner',
    #         model=model,
    #         tokenizer=tokenizer,
    #         aggregation_strategy="simple"
    #     )

    # def hide_by_nlp(self, text: str) -> str:
    #     """ Hide text using NLP NER """
    #     if self._nlp is None:
    #         self._init_ner()  # will initialize self._nlp properly
    #     assert self._nlp, self._nlp
    #     return self._mask_ner(text, self._nlp(text))

    def hide_by_personal_info(self, text: str, info: Union[PersonalInfo, dict], use_natural_placeholders: bool = False):
        """ Hide text using personal information """
        keywords: tuple
        if isinstance(info, PersonalInfo):
            keywords = (
                (info.first_name, '<NAME>'),
                (info.last_name, '<NAME>'),
                (info.birth_name, '<NAME>'),
                (info.ipp, '<IPP>'),
                (info.postal_code, '<CODE_POSTAL>'),
                (info.birthdate.strftime('%m/%d/%Y'), '<DATE>'),
                (info.birthdate.strftime('%m %d %Y'), '<DATE>'),
                (info.birthdate.strftime('%m:%d:%Y'), '<DATE>'),
                (info.birthdate.strftime('%m-%d-%Y'), '<DATE>'),
                (info.birthdate.strftime('%Y-%m-%d'), '<DATE>'),
            )
        else:  # it's a dict
            keywords = tuple((k, v) for k, v in info.items())

        return self.hide_by_keywords(text, [
            (info, (NATURAL_PLACEHOLDERS[tag]
             if use_natural_placeholders else tag))
            for info, tag in keywords if info
        ])

    def hide_by_keywords(self, text: str, keywords: Iterable[tuple[str, str]]):
        """ Hide text using keywords """
        processor = KeywordProcessor()
        for key, mask in keywords:
            processor.add_keyword(key, mask)

        return processor.replace_keywords(text)

    def hide_by_regex(self, text: str, use_natural_placeholders: bool = False) -> str:
        """Hide text using regular expression """
        if use_natural_placeholders:
            patterns = {
                reg: NATURAL_PLACEHOLDERS[tag]
                for reg, tag in PATTERNS.items()
            }
        else:
            patterns = PATTERNS
        return utils.multi_subs_by_regex(text, patterns)

    # def _mask_ner(self, text: str, matches: list) -> str:
    #     """ hide objects matched by nlp  """
    #     starters = (  # matches often include previous space
    #         m['start'] + (1 if text[m['start']] == ' ' else 0)
    #         for m in matches
    #     )
    #     return utils.multi_subs_by_match(text, starters, ('<'+m['entity_group']+'>' for m in matches), (m['end'] for m in matches))

    # def run_straight_algorithm(self, text: str, info: dict) -> str:
    #     "Run regexes, then finishes the job with NER"
    #     content = self.hide_by_personal_info(text, info)
    #     content = self.hide_by_regex(content)
    #     content = self.hide_by_nlp(content)
    #     return content

    # def run_sneaky_algorithm(self, text: str, info: dict) -> str:
    #     """Use natural placeholder instead of tags, in order to get the NER to work on known data, and finishes by replace the natural placeholders by tags, in case the NER didn't recognize them."""
    #     content = self.hide_by_personal_info(
    #         text, info, use_natural_placeholders=True)
    #     content = self.hide_by_regex(content, use_natural_placeholders=True)
    #     content = self.hide_by_nlp(content)
    #     content = self.replaced_placeholders_by_tags(content)
    #     return content

    def replaced_placeholders_by_tags(self, text: str) -> str:
        "Replace in-place natural placeholders found in given text by their tags, i.e. Margaret Hamilton by <NAME>"
        return self.hide_by_keywords(text, ((phldr, tag) for tag, phldr in NATURAL_PLACEHOLDERS.items()))

    # def run_confident_snake_algorithm(self, text: str, info: dict) -> str:
    #     """Behave exactly like the sneaky algorithm, but trust the NER and don't replace placeholder after it (this method is mainly here to ensure correct behavior from the sneaky solution)"""
    #     content = self.hide_by_personal_info(
    #         text, info, use_natural_placeholders=True)
    #     content = self.hide_by_regex(content, use_natural_placeholders=True)
    #     content = self.hide_by_nlp(content)
    #     return content

    def run_dummy_algorithm(self, text: str, info: dict) -> str:
        """Implement a non-AI solution, by using solely regexes"""
        content = self.hide_by_personal_info(text, info)
        content = self.hide_by_regex(content)
        return content

    def anonymization_score_of(self, anonymized_text: str) -> int:
        """Compte le nombre d'occurences de la regex python `<[A-Z_]+>`"""
        assert isinstance(anonymized_text, str), (str(
            anonymized_text), repr(anonymized_text))
        return sum(1 for m in re.findall(PLACEHOLDER_REGEX, anonymized_text))

    def anonymization_methods(self) -> dict:
        return {
            **{method.name: getattr(self, f'run_{method.name}_algorithm') for method in AnonymizationMethods},
            **{method: getattr(self, f'run_{method.name}_algorithm') for method in AnonymizationMethods},
        }

    def anonymize(self, text: str, info: Union[PersonalInfo, dict] = {}, method: AnonymizationMethodsClass = None) -> str:
        func = self.anonymization_methods(
        )[method or AnonymizationMethodsClass.default()]
        return func(text, info)

    def anonymize_df_column(self, df: pl.DataFrame, to_anon_column: str, identifier_columns: dict[str, list[str]], *, target_column: Optional[str] = None,
                            remove_identifier_columns: bool = False, method: AnonymizationMethodsClass = AnonymizationMethodsClass.default()) -> pl.DataFrame:
        """In given dataframe, will anonymize all values of given column, using given columns identifiers keyed by their placeholder.

        exemple of identifier_columns: { 'NAME': ['NOM', 'PRENOM', 'NOM_NAISSANCE'] 'ID': ['IPP', 'IEP'], 'PHONE': ['TÉLÉPHONE'] }
        target_column -- if provided, will not replace the anonymized column but add another with that name
        remove_identifier_columns -- do not return columns containing identifying data

        """
        column2placeholder = {}
        for placeholder, columns in identifier_columns.items():
            for column in columns:
                column2placeholder[column] = f'<{placeholder}>'

        indexes = dict(enumerate(df.columns))  # 1: NAME  2: IPP etc
        index_of_to_anon_col = df.columns.index(to_anon_column)

        def anonymize_line(line: tuple, indexes=indexes, index_of_to_anon_col=index_of_to_anon_col):
            infos = {
                line[index]: column2placeholder[col]
                for index, col in indexes.items()
                if col in column2placeholder
            }
            return self.anonymize(line[index_of_to_anon_col], infos, method=method)

        anon_series = df.map_rows(anonymize_line).get_columns()[0]
        anonymized = df.with_columns(
            anon_series.alias(target_column or to_anon_column))
        if remove_identifier_columns:
            return anonymized.drop(list(column2placeholder))
        return anonymized
