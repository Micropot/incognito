from typing import Dict, List, Tuple
from cassis import Cas
import json

"""
    Classes to annotate the word at the given coordinates
"""


class Strategy:
    def annotate(text, coordinate: Dict[List[Tuple], str]):  # pragma: no cover
        raise NotImplementedError()


class StandoffStrategy(Strategy):
    """Generate BRAT-style standoff annotations"""

    def annotate(self, text, coordinate: Dict[List[Tuple], str]):
        lines = []
        tid = 1
        for coord_group, label in coordinate.items():
            label = label.strip("<>")
            for (start, end) in coord_group:
                span_text = text[start:end].replace("\n", " ")
                lines.append(f"T{tid}\t{label} {start} {end}\t{span_text}")
                tid += 1
        return "\n".join(lines)


class DoccanoStrategy(Strategy):
    def annotate(self, text, coordinate: Dict[List[Tuple], str]):
        """Generate Doccano jsonl format annotations"""
        label_data = []
        for spans, label in coordinate.items():
            label = label.strip("<>")
            for (start, end) in spans:
                label_data.append([start, end, label])

        # Tri optionnel des labels selon la position de début
        label_data.sort(key=lambda x: x[0])
        return json.dumps({
            "text": text,
            "label": label_data
        }, ensure_ascii=False)



class UimaCasStrategy(Strategy):
    """Stratégie pour créer des annotations au format UIMA CAS."""
    
    def __init__(self, type_name: str = 'custom.NamedEntity'):
        """
        Args:
            type_name: Nom du type d'annotation à créer dans le CAS
        """
        self.type_name = type_name
    
    def annotate(self, text: str, coordinate: Dict[Tuple[Tuple[int, int], ...], str]) -> Cas:
        """
        Crée un UIMA CAS avec les annotations fournies.
        
        Args:
            text: Le texte source
            coordinate: Dictionnaire {((start1, end1), (start2, end2), ...): '<LABEL>'}
                       Exemple: {((77, 95), (128, 151)): '<n>', ((14, 24),): '<DATE>'}
        
        Returns:
            Cas: Objet UIMA CAS avec les annotations
        """
        # Créer un CAS vide
        cas = Cas()
        
        # Ajouter le texte
        cas.sofa_string = text
        
        # Définir le type d'annotation
        typesystem = cas.typesystem
        
        # Créer un type personnalisé si nécessaire
        if not typesystem.contains_type(self.type_name):
            NamedEntityType = typesystem.create_type(
                self.type_name,
                supertypeName='uima.tcas.Annotation'
            )
            typesystem.create_feature(
                NamedEntityType,
                'label',
                'uima.cas.String'
            )
        
        # Récupérer le type
        NamedEntity = typesystem.get_type(self.type_name)
        
        # Parcourir le dictionnaire et ajouter les annotations
        for spans_tuple, label in coordinate.items():
            # Chaque spans_tuple contient un ou plusieurs (start, end)
            for start, end in spans_tuple:
                annotation = NamedEntity(begin=start, end=end, label=label)
                cas.add(annotation)
        return cas
    
    def save_to_json(self, cas: Cas, output_path: str):
        """Sauvegarde le CAS en JSON."""
        cas.to_json(output_path, pretty_print=True)
    
    def save_to_xmi(self, cas: Cas, output_path: str):
        """Sauvegarde le CAS en XMI (format XML UIMA standard)."""
        cas.to_xmi(output_path, pretty_print=True)
