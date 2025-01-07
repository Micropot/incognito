"""
    Mode pour l'anonymistaion d'un texte
"""
from __future__ import annotations
import re
from typing import Optional, Iterable
from datetime import datetime

from pydantic import BaseModel
from flashtext import KeywordProcessor


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


class Strategy:
    def anonymize(self, text):
        pass


class PiiStrategy(Strategy):
    """Remplace les infos persos"""

    def __init__(self):
        self.info: PersonalInfo = None

    def hide_by_keywords(self, text: str, keywords: Iterable[tuple[str, str]]):
        """ Hide text using keywords """
        processor = KeywordProcessor(case_sensitive=False)
        for key, mask in keywords:
            processor.add_keyword(key, mask)

        return processor.replace_keywords(text)

    def anonymize(self, text):
        keywords: tuple
        if isinstance(self.info, PersonalInfo):
            keywords = (
                (self.info.first_name, '<NAME>'),
                (self.info.last_name, '<NAME>'),
                (self.info.birth_name, '<NAME>'),
                (self.info.ipp, '<IPP>'),
                (self.info.postal_code, '<CODE_POSTAL>'),
                (self.info.birthdate.strftime('%m/%d/%Y'), '<DATE>'),
                (self.info.birthdate.strftime('%m %d %Y'), '<DATE>'),
                (self.info.birthdate.strftime('%m:%d:%Y'), '<DATE>'),
                (self.info.birthdate.strftime('%m-%d-%Y'), '<DATE>'),
                (self.info.birthdate.strftime('%Y-%m-%d'), '<DATE>'),
            )

        return self.hide_by_keywords(text, [(info, tag)for info, tag in keywords if info])


class RegexStrategy(Strategy):
    """Replace par regex"""

    def __init__(self):
        self.PATTERNS = {
            r"[12][0-9]{2}(0[1-9]|1[0-2])(2[AB]|[0-9]{2})[0-9]{3}[0-9]{3}([0-9]{2})": "<NIR>",
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b": "<EMAIL>",
            # r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}": "<PHONE>",
            r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>"
        }
        self.PLACEHOLDER_REGEX = re.compile(r'<[A-Z_]+>')

    def multi_subs_by_regex(self, text: str, repls: dict[str, str]):
        """Sub given text with each given pair repl -> regex.

        >>> multi_subs_by_regex('hello world', {r'\\w+': 'gnap', r'\\s': '! ', '$': '!'})
        'gnap! gnap!'

        Warning: repls order has an effect. Example:

        >>> multi_subs_by_regex('ab', {'a': 'c', 'b': 'a'})
        'ca'
        >>> multi_subs_by_regex('ab', {'b': 'a', 'a': 'c'})
        'cc'

        """
        for pattern, repl in repls.items():
            text = re.sub(pattern, repl, text)
        return text

    def anonymize(self, text, ) -> str:
        """Hide text using regular expression """
        patterns = self.PATTERNS
        return self.multi_subs_by_regex(text, patterns)


class Anonymizer:
    # TODO : anonymiser les dates ?
    STRATEGIES = {
        "regex": RegexStrategy(),
        "pii": PiiStrategy()
    }

    def __init__(self, text, infos):
        self.text = text

        self.used_strats = ["regex"]

        self.infos = infos
        self.infos = PersonalInfo(**infos)  # dicrt to PersonalInfo

    def anonymize_text(self):
        print("texte originale : ", self.text)

        # anonymise with strategies first then PII
        for strategy in self.used_strats:

            current_strategy = Anonymizer.STRATEGIES.get(strategy)
            print('current strat', current_strategy)
            anonymized_text = current_strategy.anonymize(self.text)

            self.text = anonymized_text
        pii_infos = PiiStrategy()
        pii_infos.info = self.infos
        self.text = pii_infos.anonymize(self.text)
        print('ano texte', self.text)
        return self.text
