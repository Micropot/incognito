from typing import Dict, List, Tuple
"""
    Classes to mask the word at the given coordinates
"""


class Strategy:
    def mask(text, coordinate: Dict[List[Tuple], str]):
        raise NotImplementedError()


class FakeStrategy(Strategy):
    """Replace word by natural placeholder"""

    def __init__(self):
        self.natural_placehodler = {
            "<PER>": "Margaret Hamilton",
            "<NAME>": "Margaret Hamilton",
            "<CODE_POSTAL>": "42000",
            "<DATE>": "1970/01/01",
            "<IPP>": "IPPPH:0987654321",
            "<NIR>": "012345678987654",
            "<EMAIL>": "place.holder@anonymization.cdc",
            "<PHONE>": "0611223344",
            "<ADRESSE>": "35 Rue Margaret Hamilton",
        }

    def mask(self, text: str, coordinate: Dict[List[Tuple], str]) -> str:
        """
        Replace in text, words at the given coordinates by a natural palceholder.

        :param test: text to anonymize
        :param coordinate: position and placehoder of the word to replace
        :returns: anonymzed text

        Example :
        >>> anonymizer = FakeStrategy()
        >>> text = "Bob"
        >>> coordinate = {((0,3),): '<NAME>',}
        >>> anonymizer.mask(text, coordinate)
        'Margaret Hamilton'
        """
        text_as_list = list(text)
        all_positions = []
        for spans, repl in coordinate.items():
            repl = self.natural_placehodler[repl]
            all_positions.extend((start, end, repl) for start, end in spans)

        all_positions.sort(key=lambda x: x[0], reverse=True)
        for start, end, repl in all_positions:
            text_as_list[start:end] = list(repl)
        return "".join(text_as_list)


class PlaceholderStrategy(Strategy):
    """Replace by placeholders"""

    def mask(self, text, coordinate: Dict[List[Tuple], str]) -> str:
        """
        Replace in text, words at the given coordinates by a placeholder.
        :param test: text to anonymize
        :param coordinate: position and placehoder of the word to replace
        :returns: anonymzed text

        Example :
        >>> anonymizer = PlaceholderStrategy()
        >>> text = "Bob"
        >>> coordinate = {((0,3),): '<NAME>',}
        >>> anonymizer.mask(text, coordinate)
        '<NAME>'

        """
        text_as_list = list(text)

        all_positions = []
        for spans, repl in coordinate.items():
            all_positions.extend((start, end, repl) for start, end in spans)

        all_positions.sort(key=lambda x: x[0], reverse=True)
        for start, end, repl in all_positions:

            text_as_list[start:end] = list(repl)
        return "".join(text_as_list)


class HideStrategy(Strategy):
    """Replace by *"""

    def mask(self, text, coordinate: Dict[List[Tuple], str]) -> str:
        """
        Replace in text, words at the given coordinates by *.
        :param test: text to anonymize
        :param coordinate: position and placehoder of the word to replace
        :returns: anonymzed text

        Example :
        >>> anonymizer = HideStrategy()
        >>> text = "Bob"
        >>> coordinate = {((0,3),): '<NAME>',}
        >>> anonymizer.mask(text, coordinate)
        '********'

        """
        text_as_list = list(text)

        all_positions = []
        for spans, repl in coordinate.items():
            all_positions.extend((start, end, repl) for start, end in spans)

        all_positions.sort(key=lambda x: x[0], reverse=True)
        for start, end, repl in all_positions:
            word_len = end - start
            replacement = "*" * (8 if word_len < 5 else word_len)
            text_as_list[start:end] = list(replacement)
        return "".join(text_as_list)


class HashStrategy(Strategy):
    """Replace les mots par leur hash"""

    # TODO : blake256 8 digits et paper bourrin(20ene de bytes)
    pass
