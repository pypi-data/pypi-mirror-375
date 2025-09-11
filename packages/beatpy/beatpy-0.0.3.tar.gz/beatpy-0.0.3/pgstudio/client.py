from typing import Dict, Tuple

import pygame
from pydantic import BaseModel

from pgstudio._core.clock import ClockPGS, DEFAULT_FPS
from pgstudio._core.window import WindowPGS
from pgstudio.scene import T_SceneBase


def init_pygame():
    """Ejecutar al inicio de la aplicación."""
    pygame.init()
    pygame.mixer.init()


class ConfigClientPGS(BaseModel):
    app_name: str
    resolution: Tuple[int, int] = (800, 600)
    fps: int = DEFAULT_FPS


class ClientPGS:
    def __init__(
            self,
            *,
            cfg: ConfigClientPGS,
            scenes: Dict[str, T_SceneBase]
    ):
        self.window = WindowPGS(app_name=cfg.app_name, resolution=cfg.resolution)
        self.clock = ClockPGS(fps=cfg.fps)
        self.scenes = scenes
        self.is_app_running = False

    def main(self, *, first_scene: str):
        scene = self.scenes[first_scene]

        self.is_app_running = True
        while self.is_app_running:
            scene._main(window=self.window, clock=self.clock)

#pygame.draw.rect(
#    self.screen,
#    (0, 200, 0),
#    pygame.Rect(20 + (step * 15), 80, 10, 10)
#)
#pygame.display.flip()
