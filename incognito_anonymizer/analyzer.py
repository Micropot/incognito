import regex
import unicodedata
from datetime import datetime
from flashtext import KeywordProcessor
from pydantic import BaseModel
from typing import Dict, Tuple
from typing import Optional, Iterable


class PersonalInfo(BaseModel):
    first_name: str = ""
    last_name: str = ""
    birth_name: Optional[str] = ""
    birthdate: datetime = datetime(year=1000, month=1, day=1)
    ipp: str = ""
    postal_code: Optional[str] = "0"
    adress: Optional[str] = ""


class AnalyzerStrategy:
    """Constructeur de la Class Strategy"""

    def analyze(text):
        raise NotImplementedError()


class PiiStrategy(AnalyzerStrategy):
    """Detect personal infos"""

    def __init__(self):
        self.info: PersonalInfo = None

    def hide_by_keywords(
        self, text: str, keywords: Iterable[Tuple[str, str]]
    ) -> Dict[Tuple[int, int], str]:
        """
        Hide text using keywords and return positions with replacements.

        :param text: text to anonymize
        :param keywords: Iterable of tuples (word, replacement).


        :returns: List of tuples where each tuple contains:
                - A tuple with the start and end positions of the word.
                - The replacement string.
        """
        processor = KeywordProcessor(case_sensitive=False)
        for key, masks in keywords:
            key = "".join((c for c in unicodedata.normalize(
                'NFD', key) if unicodedata.category(c) != 'Mn'))
            processor.add_keyword(key, masks)

        normalized_text = "".join((c for c in unicodedata.normalize(
            'NFD', text) if unicodedata.category(c) != 'Mn'))
        # Extract keywords with positions
        found_keywords = processor.extract_keywords(
            normalized_text, span_info=True)

        result = {}
        for replacement, start, end in found_keywords:
            # Wrap positions as a tuple of tuples
            key = ((start, end),)
            # if key in result:
            #     result[key] = replacement  # Handle multiple occurrences
            # else:
            result[key] = replacement
        return result

    def analyze(self, text: str) -> str:
        """
        Hide specific words based on keywords

        :param text: text to anonymize
        """
        keywords: tuple
        if isinstance(self.info, PersonalInfo):
            keywords = (
                (self.info.first_name, "<NAME>"),
                (self.info.last_name, "<NAME>"),
                (self.info.birth_name, "<NAME>"),
                (self.info.ipp, "<IPP>"),
                (self.info.postal_code, "<CODE_POSTAL>"),
                (self.info.birthdate.strftime("%m/%d/%Y"), "<DATE>"),
                (self.info.birthdate.strftime("%m %d %Y"), "<DATE>"),
                (self.info.birthdate.strftime("%m:%d:%Y"), "<DATE>"),
                (self.info.birthdate.strftime("%m-%d-%Y"), "<DATE>"),
                (self.info.birthdate.strftime("%Y-%m-%d"), "<DATE>"),
                (self.info.birthdate.strftime("%d/%m/%Y"), "<DATE>"),
                (self.info.adress, "<ADRESSE>"),
            )

        return self.hide_by_keywords(text, [(info, tag) for info, tag in keywords if info])


class RegexStrategy(AnalyzerStrategy):
    """Detect word based on regex"""

    def __init__(self):
        Xxxxx = r"[A-ZÀ-Ÿ]\p{Ll}+"
        XXxX_ = r"[A-ZÀ-Ÿ][A-ZÀ-Ÿ\p{Ll}-]"
        sep = r"(?:[ ]*|-)?"

        self.title_regex = r"([Dd][Rr][.]?|[Dd]octeur|[mM]r?[.]?|[Ii]nterne[ ]*:?|INT|[Ee]xterne[ ]*:?|[Mm]onsieur|[Mm]adame|[Rr].f.rent[ ]*:?|[P]r[.]?|[Pp]rofesseure|[Pp]rofesseur|\s[Mm]me[.]?|[Ee]nfant|[Mm]lle|[Nn]ée?)"

        self.email_pattern = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"

        self.PATTERNS = {
            # rf"(?<={self.title_regex})([\s-][A-Z]+)+([\s-][A-Z][a-z]+)+(?![a-z])": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN0>[A-ZÀ-Ÿ][A-ZÀ-Ÿ](?:{sep}(?:ep[.]|de|[A-ZÀ-Ÿ]+))*)[ ]+(?P<FN0>{Xxxxx}(?:{sep}{Xxxxx})*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<FN1>{Xxxxx}(?:{sep}{Xxxxx})*)[ ]+(?P<LN1>[A-ZÀ-Ÿ][A-ZÀ-Ÿ]+(?:{sep}(?:ep[.]|de|[A-ZÀ-Ÿ]+))*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN3>{Xxxxx}(?:(?:-|[ ]de[ ]|[ ]ep[.][ ]){Xxxxx})*)[ ]+(?P<FN2>{Xxxxx}(?:-{Xxxxx})*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN2>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<FN0>[A-ZÀ-Ÿ][.])\s+(?P<LN0>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            r"[12]\s*[0-9]{2}\s*(0[1-9]|1[0-2])\s*(2[AB]|[0-9]{2})\s*[0-9]{3}\s*[0-9]{3}\s*(?:\(?([0-9]{2})\)?)?": "<NIR>",
            r"(?:(?:\+|00)33|0)[ \t]*[1-9](?:[ \t.-]*\d{2}){4}": "<PHONE>",
            r"\b(0?[1-9]|[12]\d|3[01])(\/|-|\.)(0?[1-9]|1[0-2])\2((?:1[6-9]|[2-9]\d)\d{2})\b": "<DATE>",

            self.email_pattern: "<EMAIL>"
        }

    def multi_subs_by_regex(self, text: str) -> Dict[Tuple[Tuple[int, int]], str]:
        """
        Find word position based on regex

        :param text: text to anonymise
        :returns: List of tuples where each tuple contains:
                - A tuple with the start and end positions of the word.
                - The replacement string.
        """
        self.position = {}
        for pattern, repl in self.PATTERNS.items():
            matches = regex.findall(pattern, text, overlapped=True)
            if matches:
                spans = [match.span() for match in regex.finditer(
                    pattern, text, overlapped=True)]

                existing_keys = list(self.position.keys())

                overlapping_keys = []
                for key in existing_keys:
                    if any(span in key for span in spans) or any(k in spans for k in key):
                        overlapping_keys.append(key)

                if overlapping_keys:
                    combined_key = tuple(
                        sorted(
                            set(span for key in overlapping_keys for span in key).union(spans))
                    )

                    for key in overlapping_keys:
                        del self.position[key]

                    self.position[combined_key] = repl
                else:
                    self.position[tuple(spans)] = repl
        result = {}

        for k, v in self.position.items():
            if v != "<EMAIL>":
                result[k] = v
                continue

            email_tuples = list(k)
            ends = {}

            for (start, end) in email_tuples:
                length = end - start
                if end not in ends or length > (ends[end][1] - ends[end][0]):
                    ends[end] = (start, end)

            result[tuple(ends.values())] = "<EMAIL>"

        self.position = result

        return self.position

    def analyze(self, text: str):
        """
        Hide text using regular expression
        :param text: text to anonymize
        """
        return self.multi_subs_by_regex(text)
