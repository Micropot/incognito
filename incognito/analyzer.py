import regex
from datetime import datetime
from flashtext import KeywordProcessor
from pydantic import BaseModel
from typing import Dict, Tuple
from typing import Optional, Iterable


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    birth_name: Optional[str]
    birthdate: datetime
    ipp: str
    postal_code: Optional[str]
    adress: Optional[str]

    @staticmethod
    def from_dict(d: dict):
        return PersonalInfo(
            first_name=d.get("PRENOM_PATIENT") or "",
            last_name=d.get("NOM_USUEL_PATIENT") or "",
            birth_name=d.get("NOM_NAISSANCE") or "",
            birthdate=d.get("DATE_NAIS") or datetime(
                year=1000, month=1, day=1),
            postal_code=d.get("CODE_POSTAL", "0"),
            ipp=d.get("IPP_PATIENT") or "",
            adress=d.get("ADRESSE") or "",
        )


class Strategy:
    """Constructeur de la Class Strategy"""

    def analyze(text):
        raise NotImplementedError()


class PiiStrategy(Strategy):
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
            processor.add_keyword(key, masks)

        # Extract keywords with positions
        found_keywords = processor.extract_keywords(text, span_info=True)

        result = {}
        for replacement, start, end in found_keywords:
            # Wrap positions as a tuple of tuples
            key = ((start, end),)
            if key in result:
                result[key] = replacement  # Handle multiple occurrences
            else:
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
                (self.info.adress, "<ADRESSE>"),
            )

        return self.hide_by_keywords(text, [(info, tag) for info, tag in keywords if info])


class RegexStrategy(Strategy):
    """Detect word based on regex"""

    def __init__(self):
        Xxxxx = r"[A-Z]\p{Ll}+"
        XXxX_ = r"[A-Z][A-Z\p{Ll}-]"
        sep = r"(?:[ ]*|-)?"

        self.title_regex = r"([Dd][Rr][.]?|[Dd]octeur|[mM]r?[.]?|[Ii]nterne[ ]*:?|[Ee]xterne[ ]*:?|[Mm]onsieur|[Mm]adame|[Rr].f.rent[ ]*:?|[P]r[.]?|[Pp]rofesseure?|\s[Mm]me[.]?|[Ee]nfant|[Mm]lle|[Nn]ée?)"

        self.PATTERNS = {
            # rf"(?<={self.title_regex})([\s-][A-Z]+)+([\s-][A-Z][a-z]+)+(?![a-z])": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN0>[A-Z][A-Z](?:{sep}(?:ep[.]|de|[A-Z]+))*)[ ]+(?P<FN0>{Xxxxx}(?:{sep}{Xxxxx})*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<FN1>{Xxxxx}(?:{sep}{Xxxxx})*)[ ]+(?P<LN1>[A-Z][A-Z]+(?:{sep}(?:ep[.]|de|[A-Z]+))*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN3>{Xxxxx}(?:(?:-|[ ]de[ ]|[ ]ep[.][ ]){Xxxxx})*)[ ]+(?P<FN2>{Xxxxx}(?:-{Xxxxx})*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<LN2>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            rf"(?<={self.title_regex}[ ]+)(?P<FN0>[A-Z][.])\s+(?P<LN0>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            r"[12]\s*[0-9]{2}\s*(0[1-9]|1[0-2])\s*(2[AB]|[0-9]{2})\s*[0-9]{3}\s*[0-9]{3}\s*(?:\(?([0-9]{2})\)?)?": "<NIR>",
            r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>",
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b": "<EMAIL>",
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

        return self.position

    def analyze(self, text: str):
        """
        Hide text using regular expression
        :param text: text to anonymize
        """
        return self.multi_subs_by_regex(text)
