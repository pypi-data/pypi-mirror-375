from typing import Dict, List

import pygame

from drum_machine.const import path_drum_sounds

DEFAULT_SAMPLES_NAME = "default"
T_Pattern = Dict[str, List[int]]

class Samples:
    """TODO: Abstraer la parte del audio de pygame."""
    def __init__(self, *, samples_name: str = DEFAULT_SAMPLES_NAME):
        self.samples_name = samples_name
        self.path_samples = path_drum_sounds / samples_name
        self.sounds: Dict[str, pygame.mixer.Sound] = self._load_samples()

    def _load_samples(self):
        """Carga los sonidos de la batería."""
        return {
            p.stem: pygame.mixer.Sound(str(p))
            for p in self.path_samples.iterdir()    # TODO: Hacer con glob.
        }

    def play_instrument(self, instrument: str) -> None:
        """Reproduce el sonido del instrumento."""
        if instrument not in self.sounds:
            raise ValueError((
                "El instrumento no se encuentra cargado."
                f"Sonidos cargados: {list(self.sounds.keys())}"
            ))

        self.sounds[instrument].play()
