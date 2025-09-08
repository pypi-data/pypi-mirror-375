from collections.abc import Sequence
import enum

import nanogui


class ColorPrimaries(enum.Enum):
    BT709 = 1

    Unspecified = 2

    BT470M = 4

    BT470BG = 5

    SMTPE170M = 6

    SMTP240M = 7

    Film = 8

    BT2020 = 9

    SMTPE428 = 10

    SMTPE431 = 11

    SMTPE432 = 12

    Weird = 22

def chroma_to_rec709_matrix(arg: Sequence[nanogui.Vector2f], /) -> nanogui.Matrix3f: ...

def chroma(arg: ColorPrimaries, /) -> list[nanogui.Vector2f]: ...

def from_screen(arg: nanogui.Screen, /) -> ColorPrimaries: ...
