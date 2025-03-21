"""
Text anonymization module
"""

from __future__ import annotations
from .analyzer import PersonalInfo
from datetime import datetime
from . import analyzer
from . import mask
import json


class Anonymizer:
    """Anonymization class based on strategies formating"""

    # available strategies
    ANALYZERS = {
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

        self._infos = None
        self._position = []
        self._mask = mask.PlaceholderStrategy()
        self._analyzers = set()

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

    def set_info(self, infos: PersonalInfo):
        """
        Set personal info

        :param infos: PersonalInfo
        """
        self._infos = infos

    def set_info_from_dict(self, **kwargs):
        """
        Set dict to PersonalInfo Class

        :param infos: dict with all the Personal info values

        """
        clean_data = {
            k: ("" if v is None else v.strftime("%Y-%m-%d")
                if isinstance(v, datetime) else v)
            for k, v in kwargs.items()
        }
        info_obj = PersonalInfo(**clean_data)
        self.set_info(info_obj)
        for key, value in vars(info_obj).items():
            setattr(self, key, value)
        return self

    def add_analyzer(self, name: str):
        """
        Add analyser

        :param AnalyzerStrategy: analyzer used for anonymisation

        """
        if name in self.ANALYZERS:
            analyzer = self.ANALYZERS.get(name)
            self._analyzers.add(analyzer)
        else:
            raise Exception(f"{name} analyzer doesn't exists")

    def set_mask(self, name: str):
        """
        Set masks

        :param mask: wanted mask
        """
        if name in self.MASKS:
            self._mask = self.MASKS.get(name)

        else:
            raise Exception(f"{name} doesn't exists")

    def anonymize(self, text: str) -> str:
        """
        Global function to anonymise a text base on the choosen strategies

        :param text: text to anonymize
        :returns: anonimized text
        """
        if not text:
            text = "NaN"
        spans = {}
        for strategy in self._analyzers:
            strategy.info = self._infos
            span = strategy.analyze(text=text)
            spans.update(span)

            anonymized_text = self._mask.mask(text, spans)
            text = anonymized_text
            spans = {}
        return anonymized_text
