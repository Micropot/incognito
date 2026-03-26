import unicodedata
from datetime import datetime
from typing import Dict, Iterable, Optional, Tuple

import regex
import re
import warnings
from flashtext import KeywordProcessor
from pydantic import BaseModel


class PersonalInfo(BaseModel):
    first_name: str = ""
    last_name: str = ""
    birth_name: Optional[str] = ""
    birthdate: datetime = datetime(year=1000, month=1, day=1)
    ipp: str = ""
    iep: str = ""
    postal_code: Optional[str] = "0"
    adress: Optional[str] = ""


class AnalyzerStrategy:
    """Constructeur de la Class Strategy"""

    def analyze(text: str, info: PersonalInfo = None):
        raise NotImplementedError()


class PiiStrategy(AnalyzerStrategy):
    """Detect personal infos"""

    def __init__(self):
        pass

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
            key = "".join(
                (
                    c
                    for c in unicodedata.normalize("NFD", key)
                    if unicodedata.category(c) != "Mn"
                )
            )
            processor.add_keyword(key, masks)

        normalized_text = "".join(
            (
                c
                for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )
        )
        # Extract keywords with positions
        found_keywords = processor.extract_keywords(normalized_text, span_info=True)

        result = {}
        for replacement, start, end in found_keywords:
            # Wrap positions as a tuple of tuples
            key = ((start, end),)
            # if key in result:
            #     result[key] = replacement  # Handle multiple occurrences
            # else:
            result[key] = replacement
        return result

    def analyze(self, text: str, info: PersonalInfo = None) -> str:
        """
        Hide specific words based on keywords

        :param text: text to anonymize
        """
        keywords: tuple
        if not isinstance(info, PersonalInfo):
            print("info must be a Personnal info type. Returning empty dict instead.")
            return {}
        keywords = (
            (info.first_name, "<NAME>"),
            (info.last_name, "<NAME>"),
            (info.birth_name, "<NAME>"),
            (info.ipp, "<IPP>"),
            (info.iep, "<IEP>"),
            (info.postal_code, "<CODE_POSTAL>"),
            (info.birthdate.strftime("%m/%d/%Y"), "<DATE>"),
            (info.birthdate.strftime("%m %d %Y"), "<DATE>"),
            (info.birthdate.strftime("%m:%d:%Y"), "<DATE>"),
            (info.birthdate.strftime("%m-%d-%Y"), "<DATE>"),
            (info.birthdate.strftime("%Y-%m-%d"), "<DATE>"),
            (info.birthdate.strftime("%d/%m/%Y"), "<DATE>"),
            (info.adress, "<ADRESSE>"),
        )

        return self.hide_by_keywords(text, [(k, t) for k, t in keywords if k])


class RegexStrategy(AnalyzerStrategy):
    """Detect word based on regex"""

    def __init__(self):
        super().__init__()
        Xxxxx = r"[A-ZÀ-Ÿ]\p{Ll}+"
        XXxX_ = r"[A-ZÀ-Ÿ][A-ZÀ-Ÿ\p{Ll}-]"
        XXxX_apostrophe = r"[A-ZÀ-Ÿ][A-ZÀ-Ÿ\p{Ll}-]*(?:[''][A-ZÀ-Ÿ][A-ZÀ-Ÿ\p{Ll}-]*)?"

        sep = r"(?:[ ]*|-)?"
        mois = r"(?i)(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|janv?[.]?|févr?[.]?|fevr?[.]?|avr[.]?|juil[.]?|sept?[.]?|oct[.]?|nov[.]?|déc[.]?|dec[.]?)"

        # Date complète littérale : "8 juillet 2020"
        self.date_litteral_full = (
            rf"\b(0?[1-9]|[12]\d|3[01])[\s]+{mois}[\s,]+((?:1[6-9]|[2-9]\d)\d{{2}})\b"
        )

        # Date partielle sans année : "20 mars"
        self.date_litteral_partial = rf"\b(0?[1-9]|[12]\d|3[01])[\s]+{mois}\b"

        # Mois seul : "juillet 2020" ou juste "juillet"
        self.mois_pattern = rf"\b{mois}(?:[\s]+((?:1[6-9]|[2-9]\d)\d{{2}}))?\b"
        self.title_regex = r"([Dd][Rr][.]?|[Dd]octeur|[mM]r?[.]?|[Ii]nterne[ ]*:?|INT|[Ee]xterne[ ]*:?|[Mm]onsieur|[Mm]adame|[Rr].f.rent[ ]*:?|[P][Rr][.]?|[Pp]rofesseure|[Pp]rofesseur|[Mm]me[.]?|[Ee]nfant|[Mm]lle|[Nn]ée?|[Cc]hef(fe)? de service|[Nn]om :)"

        self.email_pattern = (
            r"(?i)"
            r"(?:"
            r"[a-z0-9!#$%&'*+/=?^_`{|}~<>()\[\]\\:;,@\"\-]+"  # partie locale étendue
            r"(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~<>()\[\]\\:;,@\"\-]+)*"
            r"|"
            r"\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\""
            r")"
            r"@"
            r"(?:"
            r"(?:[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-](?:[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-]*[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-])?\.)*"
            r"[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-](?:[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-]*[a-z0-9*<>()\[\]!#$%&'+=?^_`{|}~-])?"
            r"|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:"
            r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\]"
            r")"
        )
        # needs a comma  or \r to match. If it's in a middle of a phrase it won't match
        self.adresse_pattern = r"(?i)\d{1,4}\s*(?:bis|ter|quater)?\s+(?:rue|avenue|av\.|boulevard|bd\.?|impasse|allée|allee|chemin|route|place|square|résidence|residence|hameau|lieu[- ]dit|voie|passage|villa|domaine|lotissement|parc|traverse|ruelle|sentier|cours|quai|esplanade)\s+[a-z0-9éèàùâêîôûïëüçæœ'\-\.]+(?:\s+[a-z0-9éèàùâêîôûïëüçæœ'\-\.]+){0,10},?\s*\d{5},?\s*[a-zéèàùâêîôûïëüçæœ'\-\.]+(?:\s+[a-zéèàùâêîôûïëüçæœ'\-\.]+){0,5}(?=\s*[,\{\n]|$)"

        # INFO: Non restrictive regexp for matching 3 word after a street description.
        self.fast_adresse_pattern = r"(?i)(?:\d+\s+)?(rue|avenue|av|boulevard|bd|bld|allée|allee|impasse|chemin|route|place|square|villa|passage|domaine|hameau|lotissement|résidence|residence|quartier|sentier|traverse|cours|quai|esplanade|promenade|rond[- ]point)\b(?:\s+\S+){1,3}"

        self.zip_city_name = (
            r"\b(\d{5})\s+([A-ZÀÂÉÈÊËÎÏÔÙÛÜÇ][A-ZÀÂÉÈÊËÎÏÔÙÛÜÇ\s\-]+)\b"
        )
        self.PATTERNS = {
            # rf"(?<={self.title_regex})([\s-][A-Z]+)+([\s-][A-Z][a-z]+)+(?![a-z])": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<LN0>[A-ZÀ-Ÿ][A-ZÀ-Ÿ](?:{sep}(?:ep[.]|de|[A-ZÀ-Ÿ]+))*)[ ]+(?P<FN0>{Xxxxx}(?:{sep}{Xxxxx})*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<FN1>{Xxxxx}(?:{sep}{Xxxxx})*)[ ]+(?P<LN1>[A-ZÀ-Ÿ][A-ZÀ-Ÿ]+(?:{sep}(?:ep[.]|de|[A-ZÀ-Ÿ]+))*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<LN3>{Xxxxx}(?:(?:-|[ ]de[ ]|[ ]ep[.][ ]){Xxxxx})*)[ ]+(?P<FN2>{Xxxxx}(?:-{Xxxxx})*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<LN2>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<FN0>[A-ZÀ-Ÿ][.])[ \t]+(?P<LN0>{XXxX_}+(?:{sep}{XXxX_}+)*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<FN0>[A-ZÀ-Ÿ][.](?:[A-ZÀ-Ÿ][.])*)\s+(?P<LN0>{XXxX_apostrophe}+(?:{sep}{XXxX_apostrophe}+)*)": "<NAME>",
            rf"(?P<TITLE>{self.title_regex}[ \n]+)(?P<FN0>[A-ZÀ-Ÿ][.](?:[A-ZÀ-Ÿ][.])*)\s+(?:de |d'|du |des )?(?P<LN0>{XXxX_apostrophe}+(?:{sep}{XXxX_apostrophe}+)*)": "<NAME>",
            # r"[12]\s*[0-9]{2}\s*(0[1-9]|1[0-2])\s*(2[AB]|[0-9]{2})\s*[0-9]{3}\s*[0-9]{3}\s*(?:\(?([0-9]{2})\)?)?": "<NIR>",
            # r"(?:(?:\+|00)33[\s.-]*|0)[\s.-]*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>",
            self.date_litteral_full: "<DATE>",  # 8 juillet 2020  ← plus spécifique en premier
            self.date_litteral_partial: "<DATE>",  # 20 mars
            self.mois_pattern: "<DATE>",
            r"\b(0?[1-9]|[12]\d|3[01])(\/|-|\.)(0?[1-9]|1[0-2])\2((?:(?:1[6-9]|[2-9]\d)\d{2}|\d{2}))\b": "<DATE>",
            self.email_pattern: "<EMAIL>",
            self.adresse_pattern: "<ADRESSE>",
            self.zip_city_name: "<ADRESSE>",
            self.mois_pattern: "<DATE>",
            r"(?:(?:\+|00)33[\s.-]*|0)[\s.-]*[1-9](?:[\s.-]*\d{2}){4}|\(?\d[\d\s]{6,}\d": "<NUMBER>",
            self.fast_adresse_pattern: "<ADRESSE>",
            # r"[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]{4,}\s+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{4,}\s": "<NAME>",
        }

        
    def _replace(self, match):
        title = match.group('TITLE') if 'TITLE' in match.groupdict() else ''
        return title + "<NAME>"

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
            matches_iter = list(regex.finditer(pattern, text, overlapped=True))
            if not matches_iter:
                continue

            # spans = [match.span() for match in matches_iter]
            spans = []
            for match in matches_iter:
                groups = match.groupdict()
                # Si on a des groupes nommés LN/FN, on prend uniquement leur span
                name_groups = [k for k in groups if (k.startswith('LN') or k.startswith('FN')) and groups[k] is not None]
                if name_groups:
                    # Prendre le span englobant tous les groupes LN/FN
                    start = min(match.start(g) for g in name_groups)
                    end = max(match.end(g) for g in name_groups)
                    spans.append((start, end))
                else:
                    spans.append(match.span())
            # Dédoublonnage : pour les spans overlappants, garder uniquement le plus long
            filtered_spans = self._remove_overlapping_spans(spans)
            existing_keys = list(self.position.keys())
            overlapping_keys = []
            for key in existing_keys:
                if any(span in key for span in filtered_spans) or any(
                    k in filtered_spans for k in key
                ):
                    overlapping_keys.append(key)

            if overlapping_keys:
                combined_key = tuple(
                    sorted(
                        set(span for key in overlapping_keys for span in key).union(
                            filtered_spans
                        )
                    )
                )
                for key in overlapping_keys:
                    del self.position[key]
                self.position[combined_key] = repl
            else:
                self.position[tuple(filtered_spans)] = repl

        result = {}
        for k, v in self.position.items():
            if v != "<EMAIL>":
                result[k] = v
                continue

            email_tuples = list(k)
            ends = {}

            for start, end in email_tuples:
                length = end - start
                if end not in ends or length > (ends[end][1] - ends[end][0]):
                    ends[end] = (start, end)

            result[tuple(ends.values())] = "<EMAIL>"

        self.position = self._resolve_position_conflicts(result)
        return self.position

    def analyze(self, text: str, info: PersonalInfo = None):
        """
        Hide text using regular expression
        :param text: text to anonymize
        """
        return self.multi_subs_by_regex(text)

    def _remove_overlapping_spans(self, spans: list) -> list:
        """
        Pour un ensemble de spans potentiellement overlappants,
        ne garder que les spans non-overlappants les plus longs.
        """
        if not spans:
            return spans

        # Trier par longueur décroissante (garder les plus longs en priorité)
        sorted_spans = sorted(spans, key=lambda s: s[1] - s[0], reverse=True)

        kept = []
        for span in sorted_spans:
            start, end = span
            # Vérifier si ce span overlap avec un span déjà gardé
            overlaps = any(
                not (end <= kept_start or start >= kept_end)
                for kept_start, kept_end in kept
            )
            if not overlaps:
                kept.append(span)

        # Retrier par position
        return sorted(kept, key=lambda s: s[0])

    def _spans_overlap(self, span1: Tuple[int, int], span2: Tuple[int, int]) -> bool:
        """Vérifie si deux spans se chevauchent"""
        return not (span1[1] <= span2[0] or span2[1] <= span1[0])

    def _resolve_position_conflicts(
        self, positions: Dict[Tuple[Tuple[int, int]], str]
    ) -> Dict[Tuple[Tuple[int, int]], str]:
        """
        Pour des clés de position qui se chevauchent avec la même valeur,
        ne garder que la clé avec le span le plus large.

        :param positions: dict avec des tuples de spans comme clés et des remplacements comme valeurs
        :returns: dict filtré sans conflits de positions
        """
        result = dict(positions)
        keys = list(result.keys())
        to_delete = set()

        for i, key1 in enumerate(keys):
            if key1 in to_delete:
                continue
            for key2 in keys[i + 1 :]:
                if key2 in to_delete:
                    continue
                if result[key1] != result[key2]:
                    continue

                has_overlap = any(
                    self._spans_overlap(s1, s2) for s1 in key1 for s2 in key2
                )

                if has_overlap:
                    len1 = max(end - start for start, end in key1)
                    len2 = max(end - start for start, end in key2)
                    to_delete.add(key1 if len1 < len2 else key2)

        for key in to_delete:
            del result[key]

        return result


class LossyStrategy(RegexStrategy):
    """
    Find word position based on regex

    :param text: text to anonymise
    :returns: List of tuples where each tuple contains:
            - A tuple with the start and end positions of the word.
            - The replacement string.
    .. warning::
    This strategy is intentionally lossy: it trades recall precision for
    maximum anonymization coverage. Information loss is expected and assumed.
    """

    def __init__(self):
        super().__init__()
        # self.title_regex = r"([Dd][Rr][.]?|[Dd]octeur|[mM]r?[.]?|[Ii]nterne[ ]*:?|INT|[Ee]xterne[ ]*:?|[Mm]onsieur|[Mm]adame|[Rr].f.rent[ ]*:?|[P][Rr][.]?|[Pp]rofesseure|[Pp]rofesseur|[Mm]me[.]?|[Ee]nfant|[Mm]lle|[Nn]ée?|[Cc]hef(fe)? de service|[Nn]om :)"
        self.LOSSY_PATTERNS = {
            # DUPONT Martin ou DUPONT de TOTO Martin ou DUPONT-TOTO Martin
            r"([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){2,}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){0,3}[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z][a-z-éèçùàâêîôûëïü]{2,})*": "<NAME>",
            # Martin DUPONT ou Martin DUPONT de TOTO ou Martin DUPONT-TOTO
            r"[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*[ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){2,}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){0,3}": "<NAME>",
            # J. Pierre ou J.P. Marie
            r"([A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]\.){1,3}[ \t]*[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*": "<NAME>",
            # DUPONT Jean-Philippe ou DUPONT Jean Philippe (prénom composé avec ou sans trait d'union)
            r"([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){2,}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){0,3}[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*([ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*)+": "<NAME>",
            # L Philippe ou L. Philippe (initiale suivie d'un prénom)
            r"\b[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]\.?[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*": "<NAME>",
            # Philippe LOC'H (prénom suivi d'un nom avec apostrophe)
            r"[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{2,})*[ \t]+([A-Z][A-Z'-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){2,}": "<NAME>",
            # DUPONT Martin ou DUPONT de TOTO Martin
            rf"(?:{self.title_regex}[ \t\n]+)?([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){"{2,}"}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){{0,3}}[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z][a-z-éèçùàâêîôûëïü]{{2,}})*": "<NAME>",
            # Martin DUPONT
            rf"(?:{self.title_regex}[ \t\n]+)?[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*[ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){{2,}}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){{0,3}}": "<NAME>",
            # J. Pierre ou J.P. Marie
            rf"(?:{self.title_regex}[ \t\n]+)?([A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]\.){{1,3}}[ \t]*[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*": "<NAME>",
            # DUPONT Jean-Philippe
            rf"(?:{self.title_regex}[ \t\n]+)?([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){{2,}}([ \t]+([A-Z][A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*|de|du|des|von|van|le|la)){{0,3}}[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*([ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*)+": "<NAME>",
            # L. Philippe
            rf"(?:{self.title_regex}[ \t\n]+)?\b[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]\.?[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*": "<NAME>",
            # Philippe LOC'H
            rf"(?:{self.title_regex}[ \t\n]+)?[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}}(-[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ][a-z-éèçùàâêîôûëïü]{{2,}})*[ \t]+([A-Z][A-Z'-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*){{2,}}": "<NAME>",
            # B. ALBERT (initiale + point + nom en majuscules)
            rf"(?:{self.title_regex}[ \t\n]+)?[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]\.[ \t]+[A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]{{2,}}([A-Z-ÉÈÀÂÊÎÔÛËÏÜÙÇ]*)": "<NAME>",

        }
    def multi_subs_by_regex(self, text: str) -> Dict[Tuple[Tuple[int, int]], str]:
        """
        Analyze text using an aggressive uppercase-based matching strategy.

        :param text: Text to anonymize.
        :returns: Dictionary mapping span tuples to replacement strings.

        .. warning::
            This strategy can suppress legitimate content. Any token matching
            the uppercase pattern will be replaced, regardless of whether it
            is actually a personal identifier.
        """

        self.position = {}
        text = text.replace('\x7f', '')
        for pattern, repl in self.LOSSY_PATTERNS.items():
            matches_iter = list(regex.finditer(pattern, text, overlapped=True))
            if not matches_iter:
                continue

            spans = [match.span() for match in matches_iter]
            filtered_spans = self._remove_overlapping_spans(spans)
            existing_keys = list(self.position.keys())

            overlapping_keys = [
                key
                for key in existing_keys
                if any(span in key for span in filtered_spans)
                or any(k in filtered_spans for k in key)
            ]

            if overlapping_keys:
                combined_key = tuple(
                    sorted(
                        set(span for key in overlapping_keys for span in key).union(
                            filtered_spans
                        )
                    )
                )
                for key in overlapping_keys:
                    del self.position[key]
                self.position[combined_key] = repl
            else:
                self.position[tuple(filtered_spans)] = repl

        self.position = self._resolve_position_conflicts(self.position)
        return self.position

    def analyze(self, text: str, info: PersonalInfo = None):
        """
        Hide text using regular expression
        :param text: text to anonymize
        """
        warnings.warn(
            "LossyStrategy.analyze() uses aggressive pattern matching that may cause "
            "unintended information loss. Tokens matching the uppercase pattern will be "
            "replaced unconditionally, including potential false positives such as "
            "acronyms, place names, or medical terminology. "
            "Use a more precise strategy if data integrity is critical.",
            UserWarning,
            stacklevel=2,
        )
        return self.multi_subs_by_regex(text)
