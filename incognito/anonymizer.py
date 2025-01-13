"""
    Module pour l'anonymistaion d'un texte
"""
from __future__ import annotations
import json
from . import analyzer


class Anonymizer:
    """Class d'anonymisation par choix des stratgies"""
    STRATEGIES = {
        "regex": analyzer.RegexStrategy(),
        "pii": analyzer.PiiStrategy()
    }  # Définition des différentes stratégies

    def __init__(self):

        self.infos = None

    def open_text_file(self, path: str) -> str:
        """
        Open input txt file
        Args:
            path : path of the input txt file
        """
        try:
            with open(path, 'r') as f:
                content = f.read()
            return content
        except FileExistsError as e:
            print(e)

    def open_json_file(self, path: str) -> str:
        """
        Open input json file for personal infos
        Args:
            path : path of the json file
        """
        try:
            with open(path) as f:
                data = json.load(f)
            return data
        except FileNotFoundError as e:
            print(e)

    def set_info(self, infos: dict):
        self.infos = analyzer.PersonalInfo(**infos)
        return self.infos

    def anonymize(self, text: str, use_natural_placeholders: bool = False) -> str:
        """
            Global function to anonymise a text base on the choosen strategies

            Args :
                use_natural_placehodler : if you want the default natural placeholder instead of the tag
        """
        for strategy in self.used_strats:
            current_strategy = Anonymizer.STRATEGIES.get(
                strategy)  # get the good strat class
            current_strategy.info = self.infos
            anonymized_text = current_strategy.anonymize(
                text=text, use_natural_placeholders=use_natural_placeholders)
            self.text = anonymized_text  # needed if you have multiple strategies in a row
            text = self.text
        return anonymized_text

    # def detect() -> list:
    #     """ renvoie list des debut et fin de mot """
    #     pass

    # def mask(words: list):
    #     """ Cache lesm mots en fonction du mask """

    #     mask_strategie[curent_mask].mask(words)

    # def anonymize(self, text) -> string:

    #     words = self.detect_entity()
    #     return self.mask_entity(text, words)
