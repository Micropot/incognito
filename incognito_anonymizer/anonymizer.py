"""
Text anonymization module
"""

from __future__ import annotations
import json
from . import analyzer
from . import mask


class Anonymizer:
    """Anonymization class based on strategies formating"""

    # available strategies
    STRATEGIES = {
        "regex": analyzer.RegexStrategy(),
        "pii": analyzer.PiiStrategy(),
    }

    # available masks
    MASKS = {
        "placeholder": mask.PlaceholderStrategy(),
        "fake": mask.FakeStrategy(),
        "hash": mask.HashStrategy(),
        "hide": mask.HideStrategy(),
    }

    def __init__(self):

        self.infos = None
        self.position = []

    def open_text_file(self, path: str) -> str:
        """
        Open input txt file

        :param path: path of the input txt file
        :returns: file content
        :raises FileExistsError: if given file not found
        """
        try:
            with open(path, "r") as f:
                content = f.read()
            return content
        except FileNotFoundError as e:
            print(e)
            raise

    def open_json_file(self, path: str) -> str:
        """
        Open input json file for personal infos

        :param path: path of the json file
        :returns: file content
        :raises FileExistsError: if given file not found
        """
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError as e:
            print(e)
            raise

    def set_info(self, infos: dict) -> analyzer.PersonalInfo:
        """
        Set dict to PersonalInfo Class

        :param infos: dict with all the Personal info values
        """
        self.infos = analyzer.PersonalInfo(**infos)
        return self.infos

    def set_strategies(self, strategies: list):
        """
        Set strategies

        :param list: list of wanted strategies
        """
        self.used_strats = strategies

    def set_masks(self, mask: str):
        """
        Set masks

        :param mask: wanted mask
        """
        self.used_mask = mask

    def anonymize(self, text: str) -> str:
        """
        Global function to anonymise a text base on the choosen strategies

        :param text: text to anonymize
        :returns: anonimized text
        """
        spans = {}
        for strategy in self.used_strats:
            current_strategy = Anonymizer.STRATEGIES.get(strategy)

            current_strategy.info = self.infos
            span = current_strategy.analyze(text=text)
            spans.update(span)

            current_mask = Anonymizer.MASKS.get(self.used_mask)
            anonymized_text = current_mask.mask(text, spans)
            text = anonymized_text
            spans = {}
        return anonymized_text
