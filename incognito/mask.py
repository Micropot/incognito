from typing import Dict, List, Tuple


class Strategy:
    # dictionnaire avec le type et la position
    def mask(self, text, coordinate: Dict[List[Tuple], str]):
        pass


class FakeStrategy(Strategy):
    """Remplace les mots par les valeurs de Natural_placeholder"""

    def __init__(self):
        self.natural_placehodler = {
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

    def mask(self, text, coordinate: Dict[List[Tuple], str]) -> str:
        """
        Remplace dans le texte les mots aux positions spécifiées par leurs valeurs associées.

        """
        # Convertir le texte en liste de caractères pour modifications sans conflits
        text_as_list = list(text)

        # Collecter toutes les positions avec leurs remplacements associés
        all_positions = []
        for spans, repl in coordinate.items():
            repl = self.natural_placehodler[repl]
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


class PlaceholderStrategy(Strategy):
    """Remplace par des balises """

    def mask(self, text, coordinate: Dict[List[Tuple], str]) -> str:
        """
        Remplace dans le texte les mots aux positions spécifiées par leurs valeurs associées.

        """
        # Convertir le texte en liste de caractères pour modifications sans conflits
        text_as_list = list(text)

        # Collecter toutes les positions avec leurs remplacements associés
        all_positions = []
        for spans, repl in coordinate.items():
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
