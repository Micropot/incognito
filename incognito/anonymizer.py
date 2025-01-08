"""
    Module pour l'anonymistaion d'un texte
"""
from __future__ import annotations
import argparse
import json
import re
import sys

from datetime import datetime
from flashtext import KeywordProcessor
from pydantic import BaseModel
from typing import Optional, Iterable


class AnonymiserCli:
    """Class pour utiliser le CLI"""

    @staticmethod
    def parse_cli(argv):
        # TODO : argument --fake : ajouter des natural placeholder
        # TODO : arguments --user... au lieu de infos pour mettre dans un json
        # TODO : Faire des tests unitaires par fonctions
        # Demander à Basile pour qu'il m'explique l'orga des documents sur MEVA (types, formulaires...)
        parser = argparse.ArgumentParser(description=__doc__)

        parser.add_argument(
            "--input", "--input_file",
            type=str,
            help="Chemin du fichier à anonymiser.",
            required=True
        )
        parser.add_argument(
            "--output", "--output_file",
            type=str,
            help="Chemin du fichier de sortie.",
            required=True
        )

        # subparser pour les différences entre  json et infos dans le cli
        subparser = parser.add_subparsers(
            dest="command", required=True, help="Choix entre un fichier JSON ou informations patient dans le CLI",)

        json_parser = subparser.add_parser(
            "json", help="Fournir un fichier JSON")
        json_parser.add_argument(
            "--json", "--json_file",
            type=str,
            help="Chemin du fichier json d'information.",
            required=False,
            nargs=1,
        )

        info_parser = subparser.add_parser(
            "infos", help="Fournir infos partients dans le CLI")
        info_parser.add_argument(
            "--first_name",
            type=str,
            help="Prénom du patient.",
            required=False
        )
        info_parser.add_argument(
            "--last_name",
            type=str,
            help="Nom du patient.",
            required=False
        )
        info_parser.add_argument(
            "--birthname",
            type=str,
            help="Nom de naissance du patient.",
            required=False
        )
        info_parser.add_argument(
            "--birthdate",
            type=str,
            help="Date de naissance du patient.",
            required=False
        )
        info_parser.add_argument(
            "--ipp",
            type=str,
            help="IPP du patient.",
            required=False
        )
        info_parser.add_argument(
            "--postal_code",
            type=str,
            help="Code postal du patient.",
            required=False
        )
        info_parser.add_argument(
            "--adress",
            type=str,
            help="Adresse postal du patient.",
            required=False
        )
        parser.add_argument(
            "-s", "--strategies",
            type=str,
            help="Stratégies à utiliser (default : %(default)s).",
            default=["regex", "pii"],
            nargs='*',
            choices=['regex', 'pii']
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Affiche des messages détaillés pendant l'exécution."
        )

        return parser.parse_args(argv)

    def run(self, argv):
        """Fonction principal du projet"""
        args = self.parse_cli(argv)
        input_file = args.input
        command = args.command
        output_file = args.output
        strats = args.strategies
        verbose = args.verbose
        ano = Anonymizer()
        if command == "json":
            json_file = args.json
            ano.infos = ano.open_json_file(json_file[0])
        ano.text = ano.open_text_file(input_file)
        if command == "infos":
            first_name = args.first_name
            last_name = args.last_name

            birthname = args.birthname
            birthdate = args.birthdate
            ipp = args.ipp
            postal_code = args.postal_code
            adress = args.adress
            keys = ["first_name", "last_name", "birthname",
                    "birthdate", "ipp", "postal_code", "adress"]
            values = [first_name, last_name, birthname,
                      birthdate, ipp, postal_code, adress]
            infos_dict = {key: value for key, value in zip(keys, values)}
            ano.infos = infos_dict  # add elements to dictionnary
        ano.used_strats = strats
        if verbose:
            print("Texte sans anonymisation : ", ano.text)
            print("strategies utilisées : ", strats)
        anonymized_text = ano.anonymize()
        output = open(output_file, "w")
        output.write(anonymized_text)
        output.close()

        if verbose:
            print("Texte anonymisé : ", anonymized_text)
            print("Texte enregistré ici : ", output_file)
            print("------ Terminé ------")


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

    def anonymize(self, text):
        pass


class PiiStrategy(Strategy):
    """Remplace les infos persos"""

    def __init__(self):
        self.info: PersonalInfo = None

    def hide_by_keywords(self, text: str, keywords: Iterable[tuple[str, str]]):
        """ Hide text using keywords

            Args : 

            >>> a = PiiStrategy()
            >>> text = "Salut User ca va ?"
            >>> a.hide_by_keywords(text, [("User", "<NAME>")])
            'Salut <NAME> ca va ?'
        """
        processor = KeywordProcessor(case_sensitive=False)
        for key, mask in keywords:
            processor.add_keyword(key, mask)

        return processor.replace_keywords(text)

    def anonymize(self, text):
        """
        Anonymisation par keywords
        """
        # TODO : Age + PII via gamm ipp + praticiens ?
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

        return self.hide_by_keywords(text, [(info, tag)for info, tag in keywords if info])


class RegexStrategy(Strategy):
    """Replace par regex"""

    def __init__(self):
        self.PATTERNS = {
            r"[12]\s*[0-9]{2}\s*(0[1-9]|1[0-2])\s*(2[AB]|[0-9]{2})\s*[0-9]{3}\s*[0-9]{3}\s*(?:\(?([0-9]{2})\)?)?": "<NIR>",
            r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b": "<EMAIL>",
            r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}": "<PHONE>"
        }
        self.PLACEHOLDER_REGEX = re.compile(r'<[A-Z_]+>')

    def multi_subs_by_regex(self, text: str, repls: dict[str, str]):
        """Sub given text with each given pair repl -> regex.
        """
        for pattern, repl in repls.items():
            text = re.sub(pattern, repl, text)
        return text

    def anonymize(self, text, ) -> str:
        """Hide text using regular expression """
        patterns = self.PATTERNS
        return self.multi_subs_by_regex(text, patterns)


class Anonymizer:
    """Class d'anonymisation par choix des stratgies"""
    STRATEGIES = {
        "regex": RegexStrategy(),
        "pii": PiiStrategy()
    }  # Définition des différentes stratégies

    def __init__(self):

        self.infos = None

    def open_text_file(self, path):
        """Open input txt file"""
        with open(path, 'r') as f:
            content = f.read()
        return content

    def open_json_file(self, path):
        """Open input json file for personal infos"""
        with open(path) as f:
            data = json.load(f)
        return data

    def anonymize(self):
        self.infos = PersonalInfo(**self.infos)  # dict to PersonalInfo
        for strategy in self.used_strats:

            current_strategy = Anonymizer.STRATEGIES.get(strategy)
            current_strategy.info = self.infos
            anonymized_text = current_strategy.anonymize(self.text)
            self.text = anonymized_text
        return self.text
