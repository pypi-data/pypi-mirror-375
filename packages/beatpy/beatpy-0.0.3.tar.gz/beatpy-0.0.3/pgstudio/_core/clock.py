import pygame as pg

DEFAULT_FPS = 60


class ClockPGS:
    FPS_ALLOWED = frozenset({30, 60})

    def __init__(self, *, fps: int = DEFAULT_FPS):
        if fps not in self.FPS_ALLOWED:
            raise ValueError(f"Invalid fps: {fps}")

        self._fps = fps
        self._clock = pg.time.Clock()

    def _tick(self) -> int:
        """ TODO: Esto retorna el número de ns que tardó en ejecutar?"""
        return self._clock.tick(self._fps)

    def refresh(self) -> None:
        self._tick()
        pg.display.update()