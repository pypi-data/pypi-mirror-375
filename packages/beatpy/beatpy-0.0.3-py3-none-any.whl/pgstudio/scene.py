from __future__ import annotations
from typing import TypeVar
from abc import ABC, abstractmethod
import logging

import pygame as pg

from pgstudio.color import BLACK
from pgstudio._core.window import WindowPGS
from pgstudio._core.clock import ClockPGS

logger = logging.getLogger(__name__)


T_SceneBase = TypeVar("SceneBase", bound="SceneBase")

class SceneBase(ABC):
    def __init__(self, name: str):
        self.name = name
        self.is_running = False

    def __enter__(self) -> None:
        """ Se ejecuta al `entrar` en la escena. """
        logger.info(f"[Start Scene] {self.name}")
        self.is_running = True

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """ Se ejecuta al `salir` de la escena."""
        logger.info(f"[Exit Scene] {self.name}")

    def run_fill(self) -> None:
        """ Como rellenar el fondo. Por default se pinta de negro.
        - TODO: Quizás se podría crear un objeto `Background` que
        se encargue del fondo de la escena."""
        ...
    
    def run_events(self) -> None:
        # TODO: Mover a diccionario, y simplemente ejecutar los eventos según aparezcan.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def _main(self, window: WindowPGS, clock: ClockPGS) -> None:
        """ Loop principal de la escena."""
        with self:
            while self.is_running:
                window.fill(color=BLACK)
                self.run_fill()
                self.run_events()
                self.main()
                clock.refresh()

    @abstractmethod
    def main(self) -> None:
        ...
