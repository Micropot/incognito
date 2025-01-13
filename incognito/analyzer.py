import re
import regex

from datetime import datetime
from flashtext import KeywordProcessor
from pydantic import BaseModel
from typing import Optional, Iterable
from . import mask


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
            first_name=d.get('PRENOM_PATIENT') or '',
            last_name=d.get('NOM_USUEL_PATIENT') or '',
            birth_name=d.get('NOM_NAISSANCE') or '',
            birthdate=d.get('DATE_NAIS') or datetime(
                year=1000, month=1, day=1),
            postal_code=d.get('CODE_POSTAL', '0'),
            ipp=d.get('IPP_PATIENT') or '',
            adress=d.get('ADRESSE') or '',
        )


class Strategy:
    """Constructeur de la Class Strategy"""

    def analyze(self, text):
        pass


class PiiStrategy(Strategy):
    """Remplace les infos persos"""

    def __init__(self):
        self.info: PersonalInfo = None

    def hide_by_keywords(self, text: str, keywords: Iterable[tuple[str, str]]) -> str:
        """
        Hide text using keywords

        Args:
            text : text to anonymize
            keywords : Tuple of word and his replacement


        >>> strat = PiiStrategy()
        >>> strat.hide_by_keywords("pomme", [("pomme","poire")])
        'poire'

        """
        processor = KeywordProcessor(case_sensitive=False)
        for key, masks in keywords:
            processor.add_keyword(key, masks)

        return processor.replace_keywords(text)

    def analyze(self, text: str, use_natural_placeholders: bool = False) -> str:
        """
        Anonymisation par keywords

        Args:
            text : text to anonymize
            use_natural_placehodler : if you want the default natural placeholder instead of the tag
        """
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
                (self.info.adress, '<ADRESSE>')
            )

        return self.hide_by_keywords(text, [
            (info, (mask.NATURAL_PLACEHOLDERS[tag]
             if use_natural_placeholders else tag))
            for info, tag in keywords if info
        ])


class RegexStrategy(Strategy):
    """Replace par regex"""
    # TODO : voir regex de l'AP-HP

    def __init__(self):
        # Lettre majuscule puis une ou plusieurs lettres minuscules Unicode
        Xxxxx = r"[A-Z]\p{Ll}+"
        # Lettre majuscule puis un ou plusieurs caractères qui peuvent être une majuscule, une minuscule Unicode ou un tiret
        XXxX_ = r"[A-Z][A-Z\p{Ll}-]"
        # Séparateur qui est peut être aucun caratère, zéro ou plusieurs espaces, un tiret
        sep = r"(?:[ ]*|-)?"

        self.title_regex = {r"(?:[Dd][Rr][.]?|[Dd]octeur|\s[mM]r?[.]?|[Ii]nterne[ ]*:|[Ee]xterne[ ]*:?|[Mm]onsieur|[Mm]adame|[Rr].f.rent[ ]*:?|[P]r[.]?|[Pp]rofesseure?|\s[Mm]me[.]?|[Ee]nfant|[Mm]lle)[ ]+": "<TITLE>",
                            }

        self.PATTERNS = {
            # Nom composé en Maj/min séparé de tiret
            rf"(<TITLE>|[Ii]nterne\s?|[Ee]xterne\s?)(?P<LN2>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            # Nom en maj puis prénom maj/min
            rf"(<TITLE>|[Ii]nterne\s?|[Ee]xterne\s?)(?P<LN0>[A-Z][A-Z](?:{sep}(?:ep[.]|de|[A-Z]+))*)[ ]+(?P<FN0>{Xxxxx}(?:{sep}{Xxxxx})*)": "<NAME>",
            # prénom puis nom en maj
            rf"(<TITLE>|[Ii]nterne\s?|[Ee]xterne\s?)(?P<FN1>{Xxxxx}(?:{sep}{Xxxxx})*)[ ]+(?P<LN1>[A-Z][A-Z]+(?:{sep}(?:ep[.]|de|[A-Z]+))*)": "<NAME>",
            # nom avec prépo puis prénom
            rf"(<TITLE>|[Ii]nterne\s?|[Ee]xterne\s?)(?P<LN3>{Xxxxx}(?:(?:-|[ ]de[ ]|[ ]ep[.][ ]){Xxxxx})*)[ ]+(?P<FN2>{Xxxxx}(?:-{Xxxxx})*)": "<NAME>",
            # prenom abrégré puis nom complet
            rf"(<TITLE>|[Ii]nterne\s?|[Ee]xterne\s?)(?P<FN0>[A-Z][.])\s+(?P<LN0>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",

            r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?: ?\. ?[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*") ?@ ?(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])? ?\. ?)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) ?\. ?){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""": "<EMAIL>",


            r"[12]\s*[0-9]{2}\s*(0[1-9]|1[0-2])\s*(2[AB]|[0-9]{2})\s*[0-9]{3}\s*[0-9]{3}\s*(?:\(?([0-9]{2})\)?)?": "<NIR>",

            r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>",
        }
        self.PLACEHOLDER_REGEX = re.compile(r'<[A-Z_]+>')

    def multi_subs_by_regex(self, text: str, repls: dict[str, str]) -> str:
        """Sub given text with each given pair repl -> regex.

            >>> reg = RegexStrategy()
            >>> reg.multi_subs_by_regex('hi! peoples',{'hi': 'hello', 'p[a-z]+s': 'world'})
            'hello! world'
        """

        for pattern, repl in repls.items():  # repl = Balise
            text = regex.sub(pattern, repl, text)
            print(text)
        return text

    def analyze(self, text: str, use_natural_placeholders: bool = False) -> str:
        """
        Hide text using regular expression
        Args:
            text : text to anonymize
            use_natural_placehodler : if you want the default natural placeholder instead of the tag
        """
        text = self.multi_subs_by_regex(text, self.title_regex)
        if use_natural_placeholders:
            patterns = {
                reg: mask.NATURAL_PLACEHOLDERS[tag]
                for reg, tag in self.PATTERNS.items()
            }
        else:
            patterns = self.PATTERNS
        return self.multi_subs_by_regex(text, patterns)
