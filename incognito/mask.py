from typing import Dict, List, Tuple

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

    def mask(self, text, coordinate: Dict[str, List[Tuple]]) -> str:
        """
        Remplace dans le texte les mots aux positions spécifiées par leurs valeurs associées.

        :param text: Le texte original.
        :param positions: Un dictionnaire où les clés sont les valeurs de remplacement et les valeurs
                          sont des listes de tuples (début, fin) représentant les positions.
        :return: Le texte modifié avec les remplacements effectués.

        >>> text = "hi! peoples"
        >>> positions = {'hello': [(0, 2)], 'world': [(4, 11)]}
        >>> pl = PlaceholderStrategy()
        >>> pl.mask(text, positions)
        'hello! world'
        """
        # Convertir le texte en liste de caractères pour modifications sans conflits
        text_as_list = list(text)

        # Collecter toutes les positions avec leurs remplacements associés
        all_positions = []
        for repl, spans in coordinate.items():
            all_positions.extend((start, end, repl)
                                 for start, end in spans)

        # Trier les positions par ordre décroissant de début
        all_positions.sort(key=lambda x: x[0], reverse=True)

        # Remplacer les portions correspondantes dans la liste
        for start, end, repl in all_positions:

            # Remplacer dans le texte
            text_as_list[start:end] = list(repl)

        # Reconvertir la liste en chaîne de caractères
        return ''.join(text_as_list)


class HashStrategy(Strategy):
    """Replace les mots par leur hash"""
    pass
