from __future__ import annotations
import re
import enum
import polars as pl
from typing import Optional, Union, Iterable
from datetime import datetime

from pydantic import BaseModel, PrivateAttr
from flashtext2 import KeywordProcessor


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

    def anonymize(self, text):
        pass


class RegexStrategy(Strategy):
    """Replace par regex"""

    def __init__(self):
        self.PATTERNS = {
            r"[12][0-9]{2}(0[1-9]|1[0-2])(2[AB]|[0-9]{2})[0-9]{3}[0-9]{3}([0-9]{2})": "<NIR>",
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b": "<EMAIL>",
            # r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}": "<PHONE>",
            r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>"
        }
        self.NATURAL_PLACEHOLDERS = {
            '<PER>': 'Margaret Hamilton',
            '<NAME>': 'Margaret Hamilton',
            '<CODE_POSTAL>': '42000',
            '<DATE>': '1970/01/01',
            '<IPP>': 'IPPPH:0987654321',
            '<NIR>': '012345678987654',
            '<EMAIL>': 'place.holder@anonymization.cdc',
            '<PHONE>': '0611223344',
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
    STRATEGIES = {
        "regex": RegexStrategy(),
        "pii": PiiStrategy()
    }

    def __init__(self, text):
        self.text = text

        self.used_strats = ["regex"]

    def anonymize_text(self):
        for strategy in self.used_strats:
            current_strategy = Anonymizer.STRATEGIES.get(strategy)
            anonymized_text = current_strategy.anonymize(self.text)
            print('ano texte', anonymized_text)
        return anonymized_text
