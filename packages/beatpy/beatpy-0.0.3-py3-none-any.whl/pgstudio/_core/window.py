from typing import Tuple

import pygame
import pygame as pg


class WindowPGS:
    def __init__(
            self,
            *,
            app_name: str,
            resolution: Tuple[int, int]
    ):
        self.app_name = app_name
        self.resolution = resolution
        self.win = pg.display.set_mode(resolution)
        pg.display.set_caption(app_name)

    def fill(self, *, color: Tuple[int, int, int]):
        self.win.fill(color)
