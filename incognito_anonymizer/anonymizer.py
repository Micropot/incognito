"""
Text anonymization module
"""

from __future__ import annotations
from .analyzer import PersonalInfo
from datetime import datetime
from . import analyzer
from . import mask
from . import anotate
import json


class Anonymizer:
    """Anonymization class based on strategies formating"""

    def __init__(self):
        # available strategies
        self.ANALYZERS = {
            "regex": analyzer.RegexStrategy(),
            "pii": analyzer.PiiStrategy(),
            "lossy": analyzer.LossyStrategy(),
        }

        # available masks
        self.MASKS = {
            "placeholder": mask.PlaceholderStrategy(),
            "fake": mask.FakeStrategy(),
            "hash": mask.HashStrategy(),
            "hide": mask.HideStrategy(),
        }

        # available annotator
        self.ANNOTATORS = {
            "standoff": anotate.StandoffStrategy(),
            "doccano": anotate.DoccanoStrategy(),
            "uimacas": anotate.UimaCasStrategy(),
        }

        self._infos = None
        self._position = []
        self._mask = mask.PlaceholderStrategy()
        self._analyzers = []
        self._annotator = None

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
        return infos

    def set_info_from_dict(self, **kwargs):
        """
        Set dict to PersonalInfo Class

        :param infos: dict with all the Personal info values

        """
        clean_data = {
            k: (
                ""
                if v is None
                else v.strftime("%Y-%m-%d")
                if isinstance(v, datetime)
                else v
            )
            for k, v in kwargs.items()
        }
        info_obj = PersonalInfo(**clean_data)
        self._infos = info_obj
        return info_obj

    def add_analyzer(self, name: str):
        """
        Add analyser

        :param name: analyzer used for anonymisation

        """
        if name in self.ANALYZERS:
            analyzer = self.ANALYZERS.get(name)
            if analyzer not in self._analyzers:
                self._analyzers.append(analyzer)
        else:
            raise Exception(f"{name} analyzer doesn't exist")

    def set_mask(self, name: str):
        """
        Set masks

        :param name: wanted mask
        """
        if name in self.MASKS:
            self._mask = self.MASKS.get(name)

        else:
            raise Exception(f"{name} mask doesn't exist")

    def set_annotator(self, name: str):
        """
        Set annotator

        :param name: wanted annotator
        """
        if name in self.ANNOTATORS:
            self._annotator = self.ANNOTATORS.get(name)
        else:
            raise Exception(f"{name} annotator doesn't exist")

    def anonymize(self, text: str, infos: PersonalInfo = None) -> str:
        """
        Global function to anonymise a text base on the choosen strategies

        :param text: text to anonymize
        :returns: anonimized text
        """
        if not text:
            return "NaN"
        resolved_infos = infos if infos is not None else self._infos
        anonymized_text = text
        for strategy in self._analyzers:
            spans = strategy.analyze(text=anonymized_text, info=resolved_infos)
            anonymized_text = self._mask.mask(anonymized_text, spans)
        return anonymized_text

    def annotate(self, text: str) -> str:
        """
        Global function to annotate a text base on the choosen strategies

        :param text: text to annotate
        :returns: annonated text
        """
        spans = {}
        for strategy in self._analyzers:
            strategy.info = self._infos
            span = strategy.analyze(text=text)
            spans.update(span)
        if self._annotator:
            annotated_text = self._annotator.annotate(text, spans)
        return annotated_text
