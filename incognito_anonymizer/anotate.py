from typing import Dict, List, Tuple
"""
    Classes to annotate the word at the given coordinates
"""


class Strategy:
    def annotate(text, coordinate: Dict[List[Tuple], str]):
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
        raise NotImplementedError
