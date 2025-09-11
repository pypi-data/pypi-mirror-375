from typing import List, Dict


def get_phrases(*, instruments: List[str], list_notes: List[str]) -> Dict:
    if len(instruments) != len(list_notes):
        raise Exception("Deben tener la misma longitud.")
    return {instrument: notes for instrument, notes in zip(instruments, list_notes)}
