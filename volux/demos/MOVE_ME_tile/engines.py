from random import randint
from math import ceil, floor

from .types import (
    HueParameters,
    SaturationParameters,
    BrightnessParameters,
    KelvinParameters,
)
from .engine.frame import (
    FrameEngine,
    RenderingEngineSettings,
)
from .engine.motion import MotionEngine
from .types import HSBK
from .util import clamp


class SolidFrameEngine(FrameEngine):
    """Renders a frame where every pixel is the same color."""

    def __init__(self):
        settings = RenderingEngineSettings(
            hue=HueParameters(),
            saturation=SaturationParameters(),
            brightness=BrightnessParameters(),
            kelvin=KelvinParameters(),
        )
        super().__init__(settings=settings, render_func=self._func)

    def _func(self, val, settings):
        print("settings not respected yet.")
        return [
            (0, 65535, (65535 / 1024) * val[0][0], 3500) for _ in range(64)
        ]
        # for idx, pixel in enumerate(self.frame):
        #     if idx % 2 == 0:
        #         self.frame[idx] = (
        #             (65535 / 1),
        #             65535,
        #             (65535 / 100) * (val / 100),
        #             6500,
        #         )
        #     else:
        #         if randint(0, 1) == 0:
        #             self.frame[idx] = (
        #                 (65535 / 2),
        #                 65535,
        #                 (65535 / 50) * (val / 2),
        #                 6500,
        #             )
        #         else:
        #             self.frame[idx] = (
        #                 (65535 / 3),
        #                 65535,
        #                 (65535 / 50) * (val / 2),
        #                 6500,
        #             )

        return self.frame


class NoiseFrameEngine(FrameEngine):
    def __init__(self):
        settings = RenderingEngineSettings(
            hue=HueParameters(),
            saturation=SaturationParameters(),
            brightness=BrightnessParameters(),
            kelvin=KelvinParameters(),
        )
        super().__init__(settings=settings, render_func=self._func)

    # TODO: settings not respected yet.
    def _func(self, val, settings):

        norm_combined = (val[0][0] + val[0][1]) / 2
        lowp_combined = (val[1][0] + val[1][1]) / 2

        max_probability = 10
        """(1 / this) is probability."""
        # make reactive pixels less likely when value is higher
        probability_of_reactive_pixel = int(
            max_probability * (norm_combined / 1024)
        )
        # make reactive more likely with more amplitude
        # probability_of_reactive_pixel = int(
        #     max_probability * (100 / clamp(1, val, 100))
        # )
        # print(f"reactivity probability: 1 / {probability_of_reactive_pixel}")

        tile_colors = []

        # HACK: best done with map(), I think.
        for _ in range(64):
            if randint(0, probability_of_reactive_pixel) == 1:
                tile_colors.append(
                    HSBK(
                        (65535 / 1),
                        (65535 / 100) * (randint(80, 100)),
                        (65535 / 1024) * norm_combined,
                        6500,
                    )
                )
            else:
                tile_colors.append(
                    HSBK(
                        (65535 / 2),
                        (65535 / 100) * (randint(90, 100)),
                        # (65535 / 100) * val / 10,
                        # (65535 / 100) * (19 + (31 / max(1, val))),
                        (65535 / 1024) * (1 + (19 / max(1, lowp_combined))),
                        6500,
                    )
                )

        # print(f"generated a noise frame ({'#' * ceil(val/10):10})")

        return tile_colors


class SplashMotionEngine(MotionEngine):
    """Light emits from the centre of the tile and moves towards the perimeters.

    Looks cool in a dark room.
    """

    def __init__(self):

        raise NotImplementedError("Splash Motion Engine not yet implemented.")


class NorthernMotionEngine(MotionEngine):
    """Northern Lights. Bottom Text.

    Paint the first pixel of the tile with a val-based hue and brightness, produces a trail that runs down the entire tile and slowly fades away.

    The higher the val, the longer the pixel takes to fade away while trailing down the tile.
    """

    def __init__(self):
        super().__init__(
            render_func=self._render_func, settings=RenderingEngineSettings()
        )
        self.frame = [(0, 65535, 65535 * 0.1, 3500) for _ in range(64)]
        self.i = 0

    def _render_func(self, val, settings: RenderingEngineSettings):
        # print("settings not respected yet.")
        norm_combined = (val[0][0] + val[0][1]) / 2
        lowp_combined = (val[1][0] + val[1][1]) / 2
        for idx, pixel in enumerate(self.frame):
            # if pixel[1] >= 65535:
            # else:
            #     self.frame[idx][1] += 1
            if idx == 1:
                self.frame[-1] = (
                    int((65535 / 1024) * (lowp_combined)),
                    # (int(65535 / 1024) * norm_combined + self.i) % 65535,
                    # 65535 / 2,
                    65535,
                    # randint(int((65535 / 100) * val), int((65535 / 100) * val)),
                    min((65535 / 1024) * (norm_combined * 2), 65535),
                    3500,
                )
            self.frame[idx - 1] = (
                # (self.frame[idx][0] - (self.i / 10000)) % 65535,
                self.frame[idx][0],
                # (self.frame[idx][0] + (self.i / val)) % 65535,
                # (self.frame[idx][0] - 100) % 65535,
                # (self.frame[idx][0] - (800 - (8 * val))) % 65535,
                # self.frame[idx][1],
                max(
                    0,
                    self.frame[idx][1]
                    - ((4 * ((lowp_combined / 10.24) * 1.5))),
                ),
                # self.frame[idx][2],
                max(0, self.frame[idx][2] - 800),
                self.frame[idx][3],
            )

        # print(f"shifted {'#' * int((val / 10))}")

        # incrementer = 50
        # self.i = self.i + incrementer
        # if self.i >= 65535 * incrementer:
        #     self.i = 0

        return self.frame