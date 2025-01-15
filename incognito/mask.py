from typing import Dict, List, Tuple
import regex

NATURAL_PLACEHOLDERS = {
    '<PER>': 'Margaret Hamilton',
    '<NAME>': 'Margaret Hamilton',
    '<CODE_POSTAL>': '42000',
    '<DATE>': '1970/01/01',
    '<IPP>': 'IPPPH:0987654321',
    '<NIR>': '012345678987654',
    '<EMAIL>': 'place.holder@anonymization.cdc',
    '<PHONE>': '0611223344',
    '<ADRESSE>': '35 Rue Margaret Hamilton'
}


class Strategy:
    # dictionnaire avec le type et la position
    def mask(self, text, coordinate: Dict[str, List[Tuple]]):
        pass


class FakeStrategy(Strategy):
    """Remplace les mots par les valeurs de Natural_placeholder"""

    def __init__(self):
        natural_placehodler = {
            '<PER>': 'Margaret Hamilton',
            '<NAME>': 'Margaret Hamilton',
            '<CODE_POSTAL>': '42000',
            '<DATE>': '1970/01/01',
            '<IPP>': 'IPPPH:0987654321',
            '<NIR>': '012345678987654',
            '<EMAIL>': 'place.holder@anonymization.cdc',
            '<PHONE>': '0611223344',
            '<ADRESSE>': '35 Rue Margaret Hamilton'
        }

    pass


class PlaceholderStrategy(Strategy):
    """Remplace par des balises """

    def mask(self, text: str, repls: dict[str, str]) -> str:
        for pattern, repl in repls.items():
            text = regex.sub(pattern, repl, text)
        return text


class HashStrategy(Strategy):
    """Replace les mots par leur hash"""
    pass
