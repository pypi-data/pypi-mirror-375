from typing import Literal, List, Dict, TypeVar, Type
from functools import cached_property
from pathlib import Path
from enum import Enum
import logging
import json

from pydantic import BaseModel

logger = logging.getLogger(__name__)

DEFAULT_BPM = 90
DEFAULT_NOTE_DIVISION = 4
T_Notes = str
T_Instruments = Literal[
    "hihat_closed",
    "hihat_pedal",
    "crash",
    "snare",
    "tom1",
    "tom2",
    "tom_floor",
    "kick",
]
class TInstruments(str, Enum):
    hihat_closed = "hihat_closed"
    hihat_pedal = "hihat_pedal"
    crash = "crash"
    snare = "snare"
    tom1 = "tom1"
    tom2 = "tom2"
    tom_floor = "tom_floor"
    kick = "kick"



class DrumPattern(BaseModel):
    instruments: Dict[T_Instruments, T_Notes]

    def get_instrument_hits(self, *, step: int) -> List[T_Instruments]:
        """
        Devuelve los instrumentos que deben sonar en el step dado.
        """
        hits: List[T_Instruments] = []
        for instrument, notes in self.instruments.items():
            if notes[step % len(notes)] == "1":
                hits.append(instrument)
        return hits


T_DrumPatterns = TypeVar("T_DrumPatterns", bound="DrumPatterns")

class DrumPatterns(BaseModel):
    bpm: int
    note_division: int
    patterns: List[DrumPattern]

    @cached_property
    def step_duration(self) -> float:
        """Duración de cada step en segundos según BPM y división de nota."""
        return 60 / self.bpm / self.note_division

    def __repr__(self) -> str:
        _repr = (
            "\n"
            f"[bpm] {self.bpm}\n"
            f"[note_division] {self.note_division}\n"
        )
        phrases: Dict[T_Instruments, T_Notes] = {}
        for drum_pattern in self.patterns:
            for instrument, notes in drum_pattern.instruments.items():
                if instrument not in phrases:
                    phrases[instrument] = ""
                phrases[instrument] += notes + " "  # Agrego espacio al final para que se vea visualmente.
        for instrument, notes in phrases.items():
            notes = notes.strip()
            _repr += f"{notes} | {instrument}\n"
        return _repr

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def from_phrase(
        cls: Type[T_DrumPatterns],
        bpm: int,
        note_division: int,
        phrases: Dict[TInstruments, T_Notes],
    ) -> T_DrumPatterns:
        """
        Recibe las frases completa, la suma de todos los compases y
        separa en sub-patrones de longitud `note_division`.
        """
        for instrument, phrase in phrases.items():
            if instrument not in TInstruments:
                raise ValueError(f"Instrumento inválido: {instrument}.")
            if len(phrase) % note_division != 0:
                raise ValueError((
                    f"Longitud inválida de '{instrument}': {len(phrase)} no "
                    f"divisible por note_division={note_division}"
                ))

        # Número de sub-patrones que habrá
        n_subpatterns = len(list(phrases.values())[0]) // note_division

        patterns: List[DrumPattern] = []

        # Generar cada DrumPattern combinando todos los instrumentos
        for i in range(n_subpatterns):
            instruments_slice: Dict[TInstruments, T_Notes] = {}
            for instrument, phrase in phrases.items():
                start_split = i * note_division
                end_split = start_split + note_division
                instruments_slice[instrument] = phrase[start_split:end_split]
            patterns.append(DrumPattern(instruments=instruments_slice))

        return cls(bpm=bpm, note_division=note_division, patterns=patterns)

    @classmethod
    def from_json(cls: Type[T_DrumPatterns], *, path_json: Path):
        with open(path_json, "r") as f:
            data = json.load(f)
        return cls(**data)
