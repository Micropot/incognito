"""
    Module pour l'anonymistaion d'un texte
"""
from __future__ import annotations
import json
from . import analyzer
from . import mask


class Anonymizer:
    """Class d'anonymisation par choix des stratgies"""
    STRATEGIES = {
        "regex": analyzer.RegexStrategy(),
        "pii": analyzer.PiiStrategy()
    }  # Définition des différentes stratégies

    MASKS = {
        "placeholder": mask.PlaceholderStrategy(),
        "fake": mask.FakeStrategy(),
        "hash": mask.HashStrategy(),
    }

    def __init__(self):

        self.infos = None
        self.position = []

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

    def set_info(self, infos: dict) -> analyzer.PersonalInfo:
        self.infos = analyzer.PersonalInfo(**infos)
        return self.infos

    def set_strategies(self, strategies: list):
        self.used_strats = strategies

    def set_masks(self, masks: str):
        self.used_mask = masks

    def anonymize(self, text: str, use_natural_placeholders: bool = False) -> str:
        """
            Global function to anonymise a text base on the choosen strategies

            Args :
                use_natural_placehodler : if you want the default natural placeholder instead of the tag
        """
        spans = {}
        # analyser le text pour trouver la position et le type de placehoder
        for strategy in self.used_strats:
            current_strategy = Anonymizer.STRATEGIES.get(
                strategy)  # get the good strat class

            current_strategy.info = self.infos
            span = current_strategy.analyze(
                text=text, use_natural_placeholders=use_natural_placeholders)
            spans.update(span)

        # mask les différents mots trouvés
        current_mask = Anonymizer.MASKS.get(self.used_mask)
        anonymized_text = current_mask.mask(text, spans)
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
