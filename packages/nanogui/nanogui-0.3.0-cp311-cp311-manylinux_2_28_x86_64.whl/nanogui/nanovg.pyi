import enum


class NVGwinding(enum.Enum):
    CCW = 1

    CW = 2

CCW: NVGwinding = NVGwinding.CCW

CW: NVGwinding = NVGwinding.CW

class NVGsolidity(enum.Enum):
    SOLID = 1

    HOLE = 2

SOLID: NVGsolidity = NVGsolidity.SOLID

HOLE: NVGsolidity = NVGsolidity.HOLE

class NVGlineCap(enum.Enum):
    BUTT = 0

    ROUND = 1

    SQUARE = 2

    BEVEL = 3

    MITER = 4

BUTT: NVGlineCap = NVGlineCap.BUTT

ROUND: NVGlineCap = NVGlineCap.ROUND

SQUARE: NVGlineCap = NVGlineCap.SQUARE

BEVEL: NVGlineCap = NVGlineCap.BEVEL

MITER: NVGlineCap = NVGlineCap.MITER

class NVGalign(enum.Enum):
    ALIGN_LEFT = 1

    ALIGN_CENTER = 2

    ALIGN_RIGHT = 4

    ALIGN_TOP = 8

    ALIGN_MIDDLE = 16

    ALIGN_BOTTOM = 32

    ALIGN_BASELINE = 64

ALIGN_LEFT: NVGalign = NVGalign.ALIGN_LEFT

ALIGN_CENTER: NVGalign = NVGalign.ALIGN_CENTER

ALIGN_RIGHT: NVGalign = NVGalign.ALIGN_RIGHT

ALIGN_TOP: NVGalign = NVGalign.ALIGN_TOP

ALIGN_MIDDLE: NVGalign = NVGalign.ALIGN_MIDDLE

ALIGN_BOTTOM: NVGalign = NVGalign.ALIGN_BOTTOM

ALIGN_BASELINE: NVGalign = NVGalign.ALIGN_BASELINE

class NVGblendFactor(enum.Enum):
    ZERO = 1

    ONE = 2

    SRC_COLOR = 4

    ONE_MINUS_SRC_COLOR = 8

    DST_COLOR = 16

    ONE_MINUS_DST_COLOR = 32

    SRC_ALPHA = 64

    ONE_MINUS_SRC_ALPHA = 128

    DST_ALPHA = 256

    ONE_MINUS_DST_ALPHA = 512

    SRC_ALPHA_SATURATE = 1024

ZERO: NVGblendFactor = NVGblendFactor.ZERO

ONE: NVGblendFactor = NVGblendFactor.ONE

SRC_COLOR: NVGblendFactor = NVGblendFactor.SRC_COLOR

ONE_MINUS_SRC_COLOR: NVGblendFactor = NVGblendFactor.ONE_MINUS_SRC_COLOR

DST_COLOR: NVGblendFactor = NVGblendFactor.DST_COLOR

ONE_MINUS_DST_COLOR: NVGblendFactor = NVGblendFactor.ONE_MINUS_DST_COLOR

SRC_ALPHA: NVGblendFactor = NVGblendFactor.SRC_ALPHA

ONE_MINUS_SRC_ALPHA: NVGblendFactor = NVGblendFactor.ONE_MINUS_SRC_ALPHA

DST_ALPHA: NVGblendFactor = NVGblendFactor.DST_ALPHA

ONE_MINUS_DST_ALPHA: NVGblendFactor = NVGblendFactor.ONE_MINUS_DST_ALPHA

SRC_ALPHA_SATURATE: NVGblendFactor = NVGblendFactor.SRC_ALPHA_SATURATE

class NVGcompositeOperation(enum.Enum):
    SOURCE_OVER = 0

    SOURCE_IN = 1

    SOURCE_OUT = 2

    ATOP = 3

    DESTINATION_OVER = 4

    DESTINATION_IN = 5

    DESTINATION_OUT = 6

    DESTINATION_ATOP = 7

    LIGHTER = 8

    COPY = 9

    XOR = 10

SOURCE_OVER: NVGcompositeOperation = NVGcompositeOperation.SOURCE_OVER

SOURCE_IN: NVGcompositeOperation = NVGcompositeOperation.SOURCE_IN

SOURCE_OUT: NVGcompositeOperation = NVGcompositeOperation.SOURCE_OUT

ATOP: NVGcompositeOperation = NVGcompositeOperation.ATOP

DESTINATION_OVER: NVGcompositeOperation = NVGcompositeOperation.DESTINATION_OVER

DESTINATION_IN: NVGcompositeOperation = NVGcompositeOperation.DESTINATION_IN

DESTINATION_OUT: NVGcompositeOperation = NVGcompositeOperation.DESTINATION_OUT

DESTINATION_ATOP: NVGcompositeOperation = NVGcompositeOperation.DESTINATION_ATOP

LIGHTER: NVGcompositeOperation = NVGcompositeOperation.LIGHTER

COPY: NVGcompositeOperation = NVGcompositeOperation.COPY

XOR: NVGcompositeOperation = NVGcompositeOperation.XOR

class NVGpaint:
    pass

class NVGcolor:
    pass

def RGB(arg0: int, arg1: int, arg2: int, /) -> NVGcolor: ...

def RGBf(arg0: float, arg1: float, arg2: float, /) -> NVGcolor: ...

def RGBA(arg0: int, arg1: int, arg2: int, arg3: int, /) -> NVGcolor: ...

def RGBAf(arg0: float, arg1: float, arg2: float, arg3: float, /) -> NVGcolor: ...

def LerpRGBA(arg0: NVGcolor, arg1: NVGcolor, arg2: float, /) -> NVGcolor: ...

def TransRGBA(arg0: NVGcolor, arg1: int, /) -> NVGcolor: ...

def TransRGBAf(arg0: NVGcolor, arg1: float, /) -> NVGcolor: ...

def HSL(arg0: float, arg1: float, arg2: float, /) -> NVGcolor: ...

def HSLA(arg0: float, arg1: float, arg2: float, arg3: int, /) -> NVGcolor: ...

class NVGcontext:
    def GlobalCompositeOperation(self, factor: int) -> None: ...

    def GlobalCompositeBlendFunc(self, sfactor: int, dfactor: int) -> None: ...

    def GlobalCompositeBlendFuncSeparate(self, srcRGB: int, dstRGB: int, srcAlpha: int, dstAlpha: int) -> None: ...

    def Save(self) -> None: ...

    def Restore(self) -> None: ...

    def Reset(self) -> None: ...

    def StrokeColor(self, color: NVGcolor) -> None: ...

    def StrokePaint(self, paint: NVGpaint) -> None: ...

    def FillColor(self, color: NVGcolor) -> None: ...

    def FillPaint(self, paint: NVGpaint) -> None: ...

    def MiterLimit(self, limit: float) -> None: ...

    def StrokeWidth(self, size: float) -> None: ...

    def LineCap(self, cap: int) -> None: ...

    def LineJoin(self, join: int) -> None: ...

    def GlobalAlpha(self, alpha: float) -> None: ...

    def ResetTransform(self) -> None: ...

    def Transform(self, a: float, b: float, c: float, d: float, e: float, f: float) -> None: ...

    def Translate(self, x: float, y: float) -> None: ...

    def Rotate(self, angle: float) -> None: ...

    def SkewX(self, angle: float) -> None: ...

    def SkewY(self, angle: float) -> None: ...

    def Scale(self, x: float, y: float) -> None: ...

    def CreateImage(self, filename: str, imageFlags: int) -> int: ...

    def DeleteImage(self, image: int) -> None: ...

    def LinearGradient(self, sx: float, sy: float, ex: float, ey: float, icol: NVGcolor, ocol: NVGcolor) -> NVGpaint: ...

    def BoxGradient(self, x: float, y: float, w: float, h: float, r: float, f: float, icol: NVGcolor, ocol: NVGcolor) -> NVGpaint: ...

    def RadialGradient(self, cx: float, cy: float, inr: float, outr: float, icol: NVGcolor, ocol: NVGcolor) -> NVGpaint: ...

    def ImagePattern(self, ox: float, oy: float, ex: float, ey: float, angle: float, image: int, alpha: float) -> NVGpaint: ...

    def Scissor(self, x: float, y: float, w: float, h: float) -> None: ...

    def IntersectScissor(self, x: float, y: float, w: float, h: float) -> None: ...

    def ResetScissor(self) -> None: ...

    def BeginPath(self) -> None: ...

    def MoveTo(self, x: float, y: float) -> None: ...

    def LineTo(self, x: float, y: float) -> None: ...

    def BezierTo(self, c1x: float, c1y: float, c2x: float, c2y: float, x: float, y: float) -> None: ...

    def QuadTo(self, cx: float, cy: float, x: float, y: float) -> None: ...

    def ArcTo(self, x1: float, y1: float, x2: float, y2: float, radius: float) -> None: ...

    def ClosePath(self) -> None: ...

    def PathWinding(self, dir: int) -> None: ...

    def Arc(self, cx: float, cy: float, r: float, a0: float, a1: float, dir: int) -> None: ...

    def Rect(self, x: float, y: float, w: float, h: float) -> None: ...

    def RoundedRect(self, x: float, y: float, w: float, h: float, r: float) -> None: ...

    def RoundedRectVarying(self, x: float, y: float, w: float, h: float, radTopLeft: float, radTopRight: float, radBottomRight: float, radBottomLeft: float) -> None: ...

    def Ellipse(self, cx: float, cy: float, rx: float, ry: float) -> None: ...

    def Circle(self, cx: float, cy: float, r: float) -> None: ...

    def Fill(self) -> None: ...

    def Stroke(self) -> None: ...

    def CreateFont(self, name: str, filename: str) -> int: ...

    def FindFont(self, name: str) -> int: ...

    def AddFallbackFontId(self, baseFont: int, fallbackFont: int) -> int: ...

    def AddFallbackFont(self, baseFont: str, fallbackFont: str) -> int: ...

    def FontSize(self, size: float) -> None: ...

    def FontBlur(self, blur: float) -> None: ...

    def TextLetterSpacing(self, spacing: float) -> None: ...

    def TextLineHeight(self, lineHeight: float) -> None: ...

    def TextAlign(self, align: int) -> None: ...

    def FontFaceId(self, font: int) -> None: ...

    def FontFace(self, font: str) -> None: ...

    def Text(self, x: float, y: float, string: str) -> None: ...

    def TextBounds(self, x: float, y: float, string: str) -> "std::tuple<float, float, float, float>": ...

    def TextBox(self, x: float, y: float, breakRowWidth: float, string: str) -> None: ...

    def TextBoxBounds(self, x: float, y: float, breakRowWidth: float, string: str) -> "std::tuple<float, float, float, float>": ...

    def BeginFrame(self, windowWidth: float, windowHeight: float, devicePixelRatio: float) -> None: ...

    def CancelFrame(self) -> None: ...

    def EndFrame(self) -> None: ...
