from collections.abc import Callable, Iterator, Sequence
import enum
from typing import Annotated, Optional, overload

import numpy
from numpy.typing import NDArray

from . import (
    glfw as glfw,
    icons as icons,
    ituth273 as ituth273,
    nanogui_ext as nanogui_ext,
    nanovg as nanovg
)


api: str = 'opengl'

def init(color_management: bool = False) -> None:
    r"""
    Static initialization; should be called once before invoking **any**
    NanoGUI functions **if** you are having NanoGUI manage OpenGL / GLFW.
    This method is effectively a wrapper call to ``glfwInit()``, so if you
    are managing OpenGL / GLFW on your own *do not call this method*.

    \rst Refer to :ref:`nanogui_example_3` for how you might go about
    managing OpenGL and GLFW on your own, while still using NanoGUI's
    classes. \endrst
    """

def shutdown() -> None:
    """Static shutdown; should be called before the application terminates."""

class RunMode(enum.Enum):
    """The nanogui mainloop can be in the following set of states"""

    Stopped = 0
    """The mainloop is currently stopped"""

    VSync = 2
    """Windows are redrawn based on the screen's refresh rate"""

    Eager = 3
    """Windows are redrawn as quickly as possible. Will use 100% CPU."""

    Lazy = 1
    """Windows are redrawn lazily as events arrive"""

class FileDialogType(enum.Enum):
    """Selection of file/folder dialog types supported by file_dialog()"""

    Open = 0
    """Open a single file"""

    OpenMultiple = 0
    """Open multiple files"""

    Save = 2
    """Save a single file"""

    PickFolder = 3
    """Pick a single folder (``filters`` not supported)"""

    PickFolderMultiple = 3
    """Pick multiple folders (``filters`` argument must be empty)"""

def run(run_mode: RunMode = RunMode.VSync) -> None:
    r"""
    Enter the application main loop

    Parameter ``refresh``:
        By default, NanoGUI redraws the window contents based on the screen's
        native refresh rate (e.g., 60FPS). To save power, prefer \ref
        RunMode::Lazy, which only redraws when processing of keyboard/mouse/..
        events explicitly *requests* a redraw by returning \c true. A manual
        redraw can also be triggered using \ref Screen::redraw(). The last
        option, \ref RunMode::Eager, runs the main loop while merely polling for
        events, which will use 100% CPU.
    """

def async(arg: Callable[[], None], /) -> None:
    """
    Enqueue a function to be executed executed before the application is
    redrawn the next time.

    NanoGUI is not thread-safe, and async() provides a mechanism for
    queuing up UI-related state changes from other threads.
    """

def leave() -> None:
    """
    Request the application main loop to terminate (e.g. if you detached
    mainloop).
    """

def test_10bit_edr_support() -> tuple[bool, bool]:
    """
    Check for the availability of displays with 10-bit color and/or
    extended dynamic range (EDR), i.e. the ability to reproduce
    intensities exceeding the standard dynamic range from 0.0-1.0.

    To leverage either of these features, you will need to create a Screen
    with ``float_buffer=True``. Only the macOS Metal backend of NanoGUI
    implements this function right now. All other platforms return
    ``(false, false)``.

    Returns:
        A ``std::pair`` with two boolean values. The first indicates
        10-bit color support, and the second indicates EDR support.
    """

def active() -> bool:
    """Return whether or not a main loop is currently active"""

def file_dialog(widget: Widget, type: FileDialogType, filters: Sequence[tuple[str, str]] = [], default_path: str = '') -> list[str]:
    """
    Open a native file open/save dialog.

    Parameter ``filetypes``:
        Pairs of permissible formats with descriptions like ``("png",
        "Portable Network Graphics")``.

    Parameter ``save``:
        Set to ``True`` if you would like subsequent file dialogs to open
        at whatever folder they were in when they close this one.
    """

def utf8(arg: int, /) -> str:
    r"""
    Convert a single UTF32 character code to UTF8.

    \rst NanoGUI uses this to convert the icon character codes defined in
    :ref:`file_nanogui_entypo.h`. \endrst

    Parameter ``c``:
        The UTF32 character to be converted.
    """

def load_image_directory(arg0: nanovg.NVGcontext, arg1: str, /) -> list[tuple[int, str]]:
    """
    Load a directory of PNG images and upload them to the GPU (suitable
    for use with ImagePanel)
    """

class Cursor(enum.Enum):
    """
    Cursor shapes available to use in GLFW. Shape of actual cursor
    determined by Operating System.
    """

    Arrow = 0

    IBeam = 1

    Crosshair = 2

    Hand = 3

    HResize = 4

    VResize = 5

class Alignment(enum.Enum):
    """The different kinds of alignments a layout can perform."""

    Minimum = 0

    Middle = 1

    Maximum = 2

    Fill = 3

class Orientation(enum.Enum):
    """The direction of data flow for a layout."""

    Horizontal = 0

    Vertical = 1

class Vector2i:
    @overload
    def __init__(self, arg: int, /) -> None: ...

    @overload
    def __init__(self, arg: Vector2i) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    @overload
    def __init__(self, arg0: int, arg1: int, /) -> None: ...

    def __len__(self) -> int: ...

    def __neg__(self) -> Vector2i: ...

    def __eq__(self, arg: Vector2i, /) -> bool: ...

    def __ne__(self, arg: Vector2i, /) -> bool: ...

    def __add__(self, arg: Vector2i, /) -> Vector2i: ...

    def __sub__(self, arg: Vector2i, /) -> Vector2i: ...

    def __mul__(self, arg: Vector2i, /) -> Vector2i: ...

    def __radd__(self, arg: int, /) -> Vector2i: ...

    def __rsub__(self, arg: int, /) -> Vector2i: ...

    def __rmul__(self, arg: int, /) -> Vector2i: ...

    def __rtruediv__(self, arg: int, /) -> Vector2i: ...

    def __truediv__(self, arg: Vector2i, /) -> Vector2i: ...

    def __iadd__(self, arg: Vector2i, /) -> Vector2i: ...

    def __isub__(self, arg: Vector2i, /) -> Vector2i: ...

    def __imul__(self, arg: Vector2i, /) -> Vector2i: ...

    def __itruediv__(self, arg: Vector2i, /) -> Vector2i: ...

    def __getitem__(self, index: int) -> int: ...

    def __setitem__(self, index: int, value: int) -> None: ...

    @property
    def x(self) -> int: ...

    @x.setter
    def x(self, arg: int, /) -> None: ...

    @property
    def y(self) -> int: ...

    @y.setter
    def y(self, arg: int, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

class Vector2f:
    @overload
    def __init__(self, arg: float, /) -> None: ...

    @overload
    def __init__(self, arg: Vector2f) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    @overload
    def __init__(self, arg0: float, arg1: float, /) -> None: ...

    def __len__(self) -> int: ...

    def __neg__(self) -> Vector2f: ...

    def __eq__(self, arg: Vector2f, /) -> bool: ...

    def __ne__(self, arg: Vector2f, /) -> bool: ...

    def __add__(self, arg: Vector2f, /) -> Vector2f: ...

    def __sub__(self, arg: Vector2f, /) -> Vector2f: ...

    def __mul__(self, arg: Vector2f, /) -> Vector2f: ...

    def __radd__(self, arg: float, /) -> Vector2f: ...

    def __rsub__(self, arg: float, /) -> Vector2f: ...

    def __rmul__(self, arg: float, /) -> Vector2f: ...

    def __rtruediv__(self, arg: float, /) -> Vector2f: ...

    def __truediv__(self, arg: Vector2f, /) -> Vector2f: ...

    def __iadd__(self, arg: Vector2f, /) -> Vector2f: ...

    def __isub__(self, arg: Vector2f, /) -> Vector2f: ...

    def __imul__(self, arg: Vector2f, /) -> Vector2f: ...

    def __itruediv__(self, arg: Vector2f, /) -> Vector2f: ...

    def __getitem__(self, index: int) -> float: ...

    def __setitem__(self, index: int, value: float) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

class Vector3f:
    @overload
    def __init__(self, arg: float, /) -> None: ...

    @overload
    def __init__(self, arg: Vector3f) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    @overload
    def __init__(self, arg0: float, arg1: float, arg2: float, /) -> None: ...

    def __len__(self) -> int: ...

    def __neg__(self) -> Vector3f: ...

    def __eq__(self, arg: Vector3f, /) -> bool: ...

    def __ne__(self, arg: Vector3f, /) -> bool: ...

    def __add__(self, arg: Vector3f, /) -> Vector3f: ...

    def __sub__(self, arg: Vector3f, /) -> Vector3f: ...

    def __mul__(self, arg: Vector3f, /) -> Vector3f: ...

    def __radd__(self, arg: float, /) -> Vector3f: ...

    def __rsub__(self, arg: float, /) -> Vector3f: ...

    def __rmul__(self, arg: float, /) -> Vector3f: ...

    def __rtruediv__(self, arg: float, /) -> Vector3f: ...

    def __truediv__(self, arg: Vector3f, /) -> Vector3f: ...

    def __iadd__(self, arg: Vector3f, /) -> Vector3f: ...

    def __isub__(self, arg: Vector3f, /) -> Vector3f: ...

    def __imul__(self, arg: Vector3f, /) -> Vector3f: ...

    def __itruediv__(self, arg: Vector3f, /) -> Vector3f: ...

    def __getitem__(self, index: int) -> float: ...

    def __setitem__(self, index: int, value: float) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

    @property
    def z(self) -> float: ...

    @z.setter
    def z(self, arg: float, /) -> None: ...

class Vector4f:
    @overload
    def __init__(self, arg: float, /) -> None: ...

    @overload
    def __init__(self, arg: Vector4f) -> None: ...

    @overload
    def __init__(self, arg: Sequence, /) -> None: ...

    @overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float, /) -> None: ...

    def __len__(self) -> int: ...

    def __neg__(self) -> Vector4f: ...

    def __eq__(self, arg: Vector4f, /) -> bool: ...

    def __ne__(self, arg: Vector4f, /) -> bool: ...

    def __add__(self, arg: Vector4f, /) -> Vector4f: ...

    def __sub__(self, arg: Vector4f, /) -> Vector4f: ...

    def __mul__(self, arg: Vector4f, /) -> Vector4f: ...

    def __radd__(self, arg: float, /) -> Vector4f: ...

    def __rsub__(self, arg: float, /) -> Vector4f: ...

    def __rmul__(self, arg: float, /) -> Vector4f: ...

    def __rtruediv__(self, arg: float, /) -> Vector4f: ...

    def __truediv__(self, arg: Vector4f, /) -> Vector4f: ...

    def __iadd__(self, arg: Vector4f, /) -> Vector4f: ...

    def __isub__(self, arg: Vector4f, /) -> Vector4f: ...

    def __imul__(self, arg: Vector4f, /) -> Vector4f: ...

    def __itruediv__(self, arg: Vector4f, /) -> Vector4f: ...

    def __getitem__(self, index: int) -> float: ...

    def __setitem__(self, index: int, value: float) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

    @property
    def z(self) -> float: ...

    @z.setter
    def z(self, arg: float, /) -> None: ...

    @property
    def w(self) -> float: ...

    @w.setter
    def w(self, arg: float, /) -> None: ...

class Matrix3f:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: float, /) -> None: ...

    @overload
    def __init__(self, arg: Matrix3f) -> None: ...

    @overload
    def __init__(self, arg: Annotated[NDArray[numpy.float32], dict(shape=(3, 3), device='cpu', writable=False)], /) -> None: ...

    @property
    def T(self) -> Matrix3f: ...

    def __matmul__(self, arg: Matrix3f, /) -> Matrix3f: ...

    def __len__(self) -> int: ...

    def __getitem__(self, arg: int, /) -> Vector3f: ...

    def __setitem__(self, arg0: int, arg1: Vector3f, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

    @staticmethod
    def scale(arg: Vector3f, /) -> Matrix3f: ...

    @staticmethod
    def rotate(axis: Vector3f, angle: float) -> Matrix3f: ...

class Matrix4f:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: float, /) -> None: ...

    @overload
    def __init__(self, arg: Matrix4f) -> None: ...

    @overload
    def __init__(self, arg: Annotated[NDArray[numpy.float32], dict(shape=(4, 4), device='cpu', writable=False)], /) -> None: ...

    @property
    def T(self) -> Matrix4f: ...

    def __matmul__(self, arg: Matrix4f, /) -> Matrix4f: ...

    def __len__(self) -> int: ...

    def __getitem__(self, arg: int, /) -> Vector4f: ...

    def __setitem__(self, arg0: int, arg1: Vector4f, /) -> None: ...

    def __dlpack__(self) -> NDArray[numpy.float32]: ...

    def __repr__(self) -> str: ...

    @staticmethod
    def scale(arg: Vector3f, /) -> Matrix4f: ...

    @staticmethod
    def rotate(axis: Vector3f, angle: float) -> Matrix4f: ...

    @staticmethod
    def translate(arg: Vector3f, /) -> Matrix4f: ...

    @staticmethod
    def perspective(fov: float, near: float, far: float, aspect: float = 1.0) -> Matrix4f: ...

    @staticmethod
    def ortho(left: float, right: float, bottom: float, top: float, near: float, far: float) -> Matrix4f: ...

    @staticmethod
    def look_at(origin: Vector3f, target: Vector3f, up: Vector3f) -> Matrix4f: ...

class Color:
    r"""
    \class Color common.h nanogui/common.h

    Stores an RGBA floating point color value.

    This class simply wraps around an ``Vector4f``, providing some
    convenient methods and terminology for thinking of it as a color. The
    data operates in the same way as ``Vector4f``, and the following
    values are identical:

    \rst +---------+-------------+----------------+-------------+ |
    Channel | Array Index | Vector4f field | Color field |
    +=========+=============+================+=============+ | Red | ``0``
    | x() | r() | +---------+-------------+----------------+-------------+
    | Green | ``1`` | y() | g() |
    +---------+-------------+----------------+-------------+ | Blue |
    ``2`` | z() | b() |
    +---------+-------------+----------------+-------------+ | Alpha |
    ``3`` | w() | a() |
    +---------+-------------+----------------+-------------+ \endrst
    """

    @overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int, /) -> None:
        """
        Copies (x, y, z, w) from the input vector, casting to floats and
        dividing by ``255.0``.

        Parameter ``color``:
            The three dimensional integer vector being copied, will be divided
            by ``255.0``.
        """

    @overload
    def __init__(self, arg0: int, arg1: int, /) -> None:
        """
        Copies (x, y, z) from the input vector, and sets the alpha of this
        color to be ``1.0``.

        Parameter ``color``:
            The three dimensional float vector being copied.
        """

    @overload
    def __init__(self, arg0: float, arg1: float, arg2: float, arg3: float, /) -> None:
        """
        Copies (x, y, z, w) from the input vector, casting to floats and
        dividing by ``255.0``.

        Parameter ``color``:
            The three dimensional integer vector being copied, will be divided
            by ``255.0``.
        """

    @overload
    def __init__(self, arg0: float, arg1: float, /) -> None:
        """
        Copies (x, y, z) from the input vector, and sets the alpha of this
        color to be ``1.0``.

        Parameter ``color``:
            The three dimensional float vector being copied.
        """

    def contrasting_color(self) -> Color:
        """
        Computes the luminance as ``l = 0.299r + 0.587g + 0.144b + 0.0a``. If
        the luminance is less than 0.5, white is returned. If the luminance is
        greater than or equal to 0.5, black is returned. Both returns will
        have an alpha component of 1.0.
        """

    @property
    def r(self) -> float:
        """Return a reference to the red channel"""

    @r.setter
    def r(self, arg: float, /) -> None: ...

    @property
    def g(self) -> float:
        """Return a reference to the green channel"""

    @g.setter
    def g(self, arg: float, /) -> None: ...

    @property
    def b(self) -> float:
        """Return a reference to the blue channel"""

    @b.setter
    def b(self, arg: float, /) -> None: ...

    @property
    def w(self) -> float:
        """Return a reference to the alpha channel."""

    @w.setter
    def w(self, arg: float, /) -> None: ...

    def __repr__(self) -> str: ...

class Object:
    pass

class Widget(Object):
    def __init__(self, arg: Widget) -> None:
        """Construct a new widget with the given parent widget"""

    def parent(self) -> Widget:
        """Return the parent widget"""

    def set_parent(self, arg: Widget, /) -> None:
        """Set the parent widget"""

    def layout(self) -> Layout:
        """Return the used Layout generator"""

    def set_layout(self, arg: Layout, /) -> None:
        """Set the used Layout generator"""

    def theme(self) -> Theme:
        """Return the Theme used to draw this widget"""

    def set_theme(self, arg: Theme, /) -> None:
        """Set the Theme used to draw this widget"""

    def position(self) -> Vector2i:
        """Return the position relative to the parent widget"""

    def set_position(self, arg: Vector2i, /) -> None:
        """Set the position relative to the parent widget"""

    def absolute_position(self) -> Vector2i:
        """Return the absolute position on screen"""

    def size(self) -> Vector2i:
        """Return the size of the widget"""

    def set_size(self, arg: Vector2i, /) -> None:
        """set the size of the widget"""

    def width(self) -> int:
        """Return the width of the widget"""

    def set_width(self, arg: int, /) -> None:
        """Set the width of the widget"""

    def height(self) -> int:
        """Return the height of the widget"""

    def set_height(self, arg: int, /) -> None:
        """Set the height of the widget"""

    def fixed_size(self) -> Vector2i:
        """Return the fixed size (see set_fixed_size())"""

    def set_fixed_size(self, arg: Vector2i, /) -> None:
        """
        Set the fixed size of this widget

        If nonzero, components of the fixed size attribute override any values
        computed by a layout generator associated with this widget. Note that
        just setting the fixed size alone is not enough to actually change its
        size; this is done with a call to set_size or a call to
        perform_layout() in the parent widget.
        """

    def fixed_width(self) -> int: ...

    def set_fixed_width(self, arg: int, /) -> None:
        """Set the fixed width (see set_fixed_size())"""

    def fixed_height(self) -> int: ...

    def set_fixed_height(self, arg: int, /) -> None:
        """Set the fixed height (see set_fixed_size())"""

    def visible(self) -> bool:
        """
        Return whether or not the widget is currently visible (assuming all
        parents are visible)
        """

    def set_visible(self, arg: bool, /) -> None:
        """
        Set whether or not the widget is currently visible (assuming all
        parents are visible)
        """

    def visible_recursive(self) -> bool:
        """
        Check if this widget is currently visible, taking parent widgets into
        account
        """

    def children(self) -> list[Widget]:
        """Return the list of child widgets of the current widget"""

    @overload
    def add_child(self, arg0: int, arg1: Widget, /) -> None:
        """
        Add a child widget to the current widget at the specified index.

        This function almost never needs to be called by hand, since the
        constructor of Widget automatically adds the current widget to its
        parent
        """

    @overload
    def add_child(self, arg: Widget, /) -> None:
        """Convenience function which appends a widget at the end"""

    def child_count(self) -> int:
        """Return the number of child widgets"""

    def __len__(self) -> int:
        """Return the number of child widgets"""

    def __iter__(self) -> Iterator[Widget]: ...

    def child_index(self, arg: Widget, /) -> int:
        """Returns the index of a specific child or -1 if not found"""

    def __getitem__(self, arg: int, /) -> Widget:
        """Retrieves the child at the specific position"""

    def remove_child_at(self, arg: int, /) -> None:
        """Remove a child widget by index"""

    def remove_child(self, arg: Widget, /) -> None:
        """Remove a child widget by value"""

    def __delitem__(self, arg: int, /) -> None:
        """Remove a child widget by index"""

    def enabled(self) -> bool:
        """Return whether or not this widget is currently enabled"""

    def set_enabled(self, arg: bool, /) -> None:
        """Set whether or not this widget is currently enabled"""

    def focused(self) -> bool:
        """Return whether or not this widget is currently focused"""

    def set_focused(self, arg: bool, /) -> None:
        """Set whether or not this widget is currently focused"""

    def request_focus(self) -> None:
        """Request the focus to be moved to this widget"""

    def tooltip(self) -> str: ...

    def set_tooltip(self, arg: str, /) -> None: ...

    def font_size(self) -> int:
        """
        Return current font size. If not set the default of the current theme
        will be returned
        """

    def set_font_size(self, arg: int, /) -> None:
        """Set the font size of this widget"""

    def has_font_size(self) -> bool:
        """Return whether the font size is explicitly specified for this widget"""

    def cursor(self) -> Cursor:
        """Return a pointer to the cursor of the widget"""

    def set_cursor(self, arg: Cursor, /) -> None:
        """Set the cursor of the widget"""

    def find_widget(self, arg: Vector2i, /) -> Widget:
        """Determine the widget located at the given position value (recursive)"""

    def contains(self, arg: Vector2i, /) -> bool:
        """Check if the widget contains a certain position"""

    def mouse_button_event(self, p: Vector2i, button: int, down: bool, modifiers: int) -> bool:
        """
        Handle a mouse button event (default implementation: propagate to
        children)
        """

    def mouse_motion_event(self, p: Vector2i, rel: Vector2i, button: int, modifiers: int) -> bool:
        """
        Handle a mouse motion event (default implementation: propagate to
        children)
        """

    def mouse_drag_event(self, p: Vector2i, rel: Vector2i, button: int, modifiers: int) -> bool:
        """Handle a mouse drag event (default implementation: do nothing)"""

    def mouse_enter_event(self, p: Vector2i, enter: bool) -> bool:
        """
        Handle a mouse enter/leave event (default implementation: record this
        fact, but do nothing)
        """

    def scroll_event(self, p: Vector2i, rel: Vector2f) -> bool:
        """
        Handle a mouse scroll event (default implementation: propagate to
        children)
        """

    def focus_event(self, focused: bool) -> bool:
        """
        Handle a focus change event (default implementation: record the focus
        status, but do nothing)
        """

    def keyboard_event(self, key: int, scancode: int, action: int, modifiers: int) -> bool:
        """Handle a keyboard event (default implementation: do nothing)"""

    def keyboard_character_event(self, arg: int, /) -> bool:
        """Handle text input (UTF-32 format) (default implementation: do nothing)"""

    def preferred_size(self, arg: nanovg.NVGcontext, /) -> Vector2i:
        """Compute the preferred size of the widget"""

    def preferred_size_changed(self) -> None:
        """
        Indicate that any previously cached preferred size value needs to be recomputed
        """

    def perform_layout(self, arg: nanovg.NVGcontext, /) -> None:
        """
        Invoke the associated layout generator to properly place child
        widgets, if any
        """

    def screen(self) -> Screen:
        """Walk up the hierarchy and return the parent screen"""

    def window(self) -> Window:
        """Walk up the hierarchy and return the parent window"""

    def draw(self, arg: nanovg.NVGcontext, /) -> None:
        """Draw the widget (and all child widgets)"""

class Window(Widget):
    def __init__(self, parent: Widget, title: str = 'Untitled') -> None: ...

    def title(self) -> str:
        """Return the window title"""

    def set_title(self, arg: str, /) -> None:
        """Set the window title"""

    def modal(self) -> bool:
        """Is this a model dialog?"""

    def set_modal(self, arg: bool, /) -> None:
        """Set whether or not this is a modal dialog"""

    def dispose(self) -> None:
        """Dispose the window"""

    def button_panel(self) -> Widget:
        """Return the panel used to house window buttons"""

    def center(self) -> None:
        """Center the window in the current Screen"""

class Screen(Widget):
    def __init__(self, size: Vector2i, caption: str = 'Unnamed', resizable: bool = True, maximized: bool = False, fullscreen: bool = False, depth_buffer: bool = True, stencil_buffer: bool = True, float_buffer: bool = False, gl_major: int = 3, gl_minor: int = 2) -> None:
        """
        Create a new Screen instance

        Parameter ``size``:
            Size in pixels at 96 dpi (on high-DPI screens, the actual
            resolution in terms of hardware pixels may be larger by an integer
            factor)

        Parameter ``caption``:
            Window title (in UTF-8 encoding)

        Parameter ``resizable``:
            If creating a window, should it be resizable?

        Parameter ``fullscreen``:
            Specifies whether to create a windowed or full-screen view

        Parameter ``stencil_buffer``:
            Should an 8-bit stencil buffer be allocated? NanoVG requires this
            to rasterize non-convex polygons. (NanoGUI does not render such
            polygons, but your application might.)

        Parameter ``float_buffer``:
            Should NanoGUI try to allocate a floating point framebuffer? This
            is useful for HDR and wide-gamut displays.

        Parameter ``gl_major``:
            The requested OpenGL Major version number. The default is 3, if
            changed the value must correspond to a forward compatible core
            profile (for portability reasons). For example, set this to 4 and
            gl_minor to 1 for a forward compatible core OpenGL 4.1 profile.
            Requesting an invalid profile will result in no context (and
            therefore no GUI) being created. This attribute is ignored when
            targeting OpenGL ES 2 or Metal.

        Parameter ``gl_minor``:
            The requested OpenGL Minor version number. The default is 2, if
            changed the value must correspond to a forward compatible core
            profile (for portability reasons). For example, set this to 1 and
            gl_major to 4 for a forward compatible core OpenGL 4.1 profile.
            Requesting an invalid profile will result in no context (and
            therefore no GUI) being created. This attribute is ignored when
            targeting OpenGL ES 2 or Metal.
        """

    def caption(self) -> str:
        """Get the window title bar caption"""

    def set_caption(self, arg: str, /) -> None:
        """Set the window title bar caption"""

    def background(self) -> Color:
        """Return the screen's background color"""

    def set_background(self, arg: Color, /) -> None:
        """Set the screen's background color"""

    def set_visible(self, arg: bool, /) -> None:
        """Set the top-level window visibility (no effect on full-screen windows)"""

    def set_size(self, arg: Vector2i, /) -> None:
        """Set window size"""

    def framebuffer_size(self) -> Vector2i:
        """
        Return the framebuffer size (potentially larger than size() on high-
        DPI screens)
        """

    def perform_layout(self) -> None:
        """Compute the layout of all widgets"""

    def redraw(self) -> None:
        """
        Send an event that will cause the screen to be redrawn at the next
        event loop iteration
        """

    def clear(self) -> None:
        """
        Clear the screen with the background color (glClearColor, glClear,
        etc.)

        You typically won't need to call this function yourself, as it is
        called by the default implementation of draw_contents() (which is
        called by draw_all())
        """

    def draw_all(self) -> None:
        """
        Redraw the screen if the redraw flag is set

        This function does everything -- it calls draw_setup(),
        draw_contents() (which also clears the screen by default), draw(), and
        finally draw_teardown().

        See also:
            redraw
        """

    def draw_contents(self) -> None:
        """
        Calls clear() and draws the window contents --- put your rendering
        code here.
        """

    def resize_event(self, size: Vector2i) -> bool:
        """Window resize event handler"""

    def resize_callback(self) -> Callable[[Vector2i], None]: ...

    def maximize_event(self, arg: bool, /) -> bool:
        """Window maximize event handler"""

    def set_resize_callback(self, arg: Callable[[Vector2i], None], /) -> None: ...

    def drop_event(self, arg: Sequence[str], /) -> bool:
        """Handle a file drop event"""

    def mouse_pos(self) -> Vector2i:
        """Return the last observed mouse position value"""

    def pixel_ratio(self) -> float:
        """
        Return the ratio between pixel and device coordinates (e.g. >= 2 on
        Mac Retina displays)
        """

    def has_depth_buffer(self) -> bool:
        """Does the framebuffer have a depth buffer"""

    def has_stencil_buffer(self) -> bool:
        """Does the framebuffer have a stencil buffer"""

    def has_float_buffer(self) -> bool:
        """Does the framebuffer use a floating point representation"""

    def move_window(self, arg: Vector2i, /) -> None:
        """Move window relatively"""

    def glfw_window(self) -> glfw.Window:
        """Return a pointer to the underlying GLFW window data structure"""

    def nvg_context(self) -> nanovg.NVGcontext:
        """Return a pointer to the underlying NanoVG draw context"""

    def pixel_format(self) -> Texture.PixelFormat:
        """Return the pixel format underlying the screen"""

    def component_format(self) -> Texture.ComponentFormat:
        """Return the component format underlying the screen"""

    def nvg_flush(self) -> None:
        """Flush all queued up NanoVG rendering commands"""

    def mouse_motion_event_f(self, p: Vector2f, rel: Vector2f, button: int, modifiers: int) -> bool:
        """Like mouse_motion_event(), but also capture fractional motion"""

    def applies_color_management(self) -> bool:
        """Does the floatbuffer use linear sRGB instead of regular sRGB?"""

class Layout(Object):
    def preferred_size(self, arg0: nanovg.NVGcontext, arg1: Widget, /) -> Vector2i:
        """
        Compute the preferred size for a given layout and widget

        Parameter ``ctx``:
            The ``NanoVG`` context being used for drawing.

        Parameter ``widget``:
            Widget, whose preferred size should be computed

        Returns:
            The preferred size, accounting for things such as spacing, padding
            for icons, etc.
        """

    def perform_layout(self, arg0: nanovg.NVGcontext, arg1: Widget, /) -> None:
        """
        Performs applies all layout computations for the given widget.

        Parameter ``ctx``:
            The ``NanoVG`` context being used for drawing.

        Parameter ``widget``:
            The Widget whose child widgets will be positioned by the layout
            class..
        """

class BoxLayout(Layout):
    def __init__(self, orientation: Orientation, alignment: Alignment = Alignment.Middle, margin: int = 0, spacing: int = 0) -> None:
        """
        Construct a box layout which packs widgets in the given
        ``Orientation``

        Parameter ``orientation``:
            The Orientation this BoxLayout expands along

        Parameter ``alignment``:
            Widget alignment perpendicular to the chosen orientation

        Parameter ``margin``:
            Margin around the layout container

        Parameter ``spacing``:
            Extra spacing placed between widgets
        """

    def orientation(self) -> Orientation:
        """The Orientation this BoxLayout is using."""

    def set_orientation(self, arg: Orientation, /) -> None:
        """Sets the Orientation of this BoxLayout."""

    def alignment(self) -> Alignment:
        """The Alignment of this BoxLayout."""

    def set_alignment(self, arg: Alignment, /) -> None:
        """Sets the Alignment of this BoxLayout."""

    def margin(self) -> int:
        """The margin of this BoxLayout."""

    def set_margin(self, arg: int, /) -> None:
        """Sets the margin of this BoxLayout."""

    def spacing(self) -> int:
        """The spacing this BoxLayout is using to pad in between widgets."""

    def set_spacing(self, arg: int, /) -> None:
        """Sets the spacing of this BoxLayout."""

class GroupLayout(Layout):
    def __init__(self, margin: int = 15, spacing: int = 6, group_spacing: int = 14, group_indent: int = 20) -> None:
        """
        Creates a GroupLayout.

        Parameter ``margin``:
            The margin around the widgets added.

        Parameter ``spacing``:
            The spacing between widgets added.

        Parameter ``group_spacing``:
            The spacing between groups (groups are defined by each Label
            added).

        Parameter ``group_indent``:
            The amount to indent widgets in a group (underneath a Label).
        """

    def margin(self) -> int:
        """The margin of this GroupLayout."""

    def set_margin(self, arg: int, /) -> None:
        """Sets the margin of this GroupLayout."""

    def spacing(self) -> int:
        """The spacing between widgets of this GroupLayout."""

    def set_spacing(self, arg: int, /) -> None:
        """Sets the spacing between widgets of this GroupLayout."""

    def group_indent(self) -> int:
        """
        The indent of widgets in a group (underneath a Label) of this
        GroupLayout.
        """

    def set_group_indent(self, arg: int, /) -> None:
        """
        Sets the indent of widgets in a group (underneath a Label) of this
        GroupLayout.
        """

    def group_spacing(self) -> int:
        """The spacing between groups of this GroupLayout."""

    def set_group_spacing(self, arg: int, /) -> None:
        """Sets the spacing between groups of this GroupLayout."""

class GridLayout(Layout):
    def __init__(self, orientation: Orientation = Orientation.Horizontal, resolution: int = 2, alignment: Alignment = Alignment.Middle, margin: int = 0, spacing: int = 0) -> None:
        """
        Create a 2-column grid layout by default.

        Parameter ``orientation``:
            The fixed dimension of this GridLayout.

        Parameter ``resolution``:
            The number of rows or columns in the grid (depending on the
            Orientation).

        Parameter ``alignment``:
            How widgets should be aligned within each grid cell.

        Parameter ``margin``:
            The amount of spacing to add around the border of the grid.

        Parameter ``spacing``:
            The amount of spacing between widgets added to the grid.
        """

    def orientation(self) -> Orientation:
        """The Orientation of this GridLayout."""

    def set_orientation(self, arg: Orientation, /) -> None:
        """Sets the Orientation of this GridLayout."""

    def resolution(self) -> int:
        """
        The number of rows or columns (depending on the Orientation) of this
        GridLayout.
        """

    def set_resolution(self, arg: int, /) -> None:
        """
        Sets the number of rows or columns (depending on the Orientation) of
        this GridLayout.
        """

    def margin(self) -> int:
        """The margin around this GridLayout."""

    def set_margin(self, arg: int, /) -> None:
        """Sets the margin of this GridLayout."""

    def spacing(self, arg: int, /) -> int:
        """
        The spacing at the specified axis (row or column number, depending on
        the Orientation).
        """

    @overload
    def set_spacing(self, arg: int, /) -> None:
        """Sets the spacing for a specific axis."""

    @overload
    def set_spacing(self, arg0: int, arg1: int, /) -> None:
        """Sets the spacing for all axes."""

    def alignment(self, arg0: int, arg1: int, /) -> Alignment:
        """
        The Alignment of the specified axis (row or column number, depending
        on the Orientation) at the specified index of that row or column.
        """

    @overload
    def set_col_alignment(self, arg: Alignment, /) -> None:
        """Sets the Alignment of the columns."""

    @overload
    def set_col_alignment(self, arg: Sequence[Alignment], /) -> None: ...

    @overload
    def set_row_alignment(self, arg: Alignment, /) -> None:
        """Sets the Alignment of the rows."""

    @overload
    def set_row_alignment(self, arg: Sequence[Alignment], /) -> None: ...

class AdvancedGridLayout(Layout):
    def __init__(self, widths: Sequence[int], heights: Sequence[int], margin: int = 0) -> None:
        """
        Creates an AdvancedGridLayout with specified columns, rows, and
        margin.
        """

    def row_count(self) -> int:
        """Return the number of rows"""

    def col_count(self) -> int:
        """Return the number of cols"""

    def margin(self) -> int:
        """The margin of this AdvancedGridLayout."""

    def set_margin(self, arg: int, /) -> None:
        """Sets the margin of this AdvancedGridLayout."""

    def append_row(self, size: int, stretch: float = 0) -> None:
        """Append a row of the given size (and stretch factor)"""

    def append_col(self, size: int, stretch: float = 0) -> None:
        """Append a column of the given size (and stretch factor)"""

    def set_row_stretch(self, arg0: int, arg1: float, /) -> None:
        """Set the stretch factor of a given row"""

    def set_col_stretch(self, arg0: int, arg1: float, /) -> None:
        """Set the stretch factor of a given column"""

    def set_anchor(self, arg0: Widget, arg1: AdvancedGridLayout.Anchor, /) -> None:
        """Specify the anchor data structure for a given widget"""

    def anchor(self, arg: Widget, /) -> AdvancedGridLayout.Anchor:
        """Retrieve the anchor data structure for a given widget"""

    class Anchor:
        @overload
        def __init__(self, x: int, y: int, horiz: Alignment = Alignment.Fill, vert: Alignment = Alignment.Fill) -> None:
            """Create an Anchor at position ``(x, y)`` with specified Alignment."""

        @overload
        def __init__(self, x: int, y: int, w: int, h: int, horiz: Alignment = Alignment.Fill, vert: Alignment = Alignment.Fill) -> None:
            """
            Create an Anchor at position ``(x, y)`` of size ``(w, h)`` with
            specified alignments.
            """

class Label(Widget):
    def __init__(self, parent: Widget, caption: str, font: str = 'sans', font_size: int = -1) -> None: ...

    def caption(self) -> str:
        """Get the label's text caption"""

    def set_caption(self, arg: str, /) -> None:
        """Set the label's text caption"""

    def font(self) -> str:
        """Get the currently active font"""

    def set_font(self, arg: str, /) -> None:
        """
        Set the currently active font (2 are available by default: 'sans' and
        'sans-bold')
        """

    def color(self) -> Color:
        """Get the label color"""

    def set_color(self, arg: Color, /) -> None:
        """Set the label color"""

class Popup(Window):
    def __init__(self, parent: Widget, parent_window: Optional[Window]) -> None:
        """
        Create a new popup parented to a screen (first argument) and a parent
        window (if applicable)
        """

    def anchor_pos(self) -> Vector2i:
        """
        Set the anchor position in the parent window; the placement of the
        popup is relative to it
        """

    def set_anchor_pos(self, arg: Vector2i, /) -> None:
        """
        Return the anchor position in the parent window; the placement of the
        popup is relative to it
        """

    def anchor_offset(self) -> int:
        """
        Return the anchor height; this determines the vertical shift relative
        to the anchor position
        """

    def set_anchor_offset(self, arg: int, /) -> None:
        """
        Set the anchor height; this determines the vertical shift relative to
        the anchor position
        """

    def anchor_size(self) -> int:
        """Return the anchor width"""

    def set_anchor_size(self, arg: int, /) -> None:
        """Set the anchor width"""

    def parent_window(self) -> Window:
        """Return the parent window of the popup"""

    def side(self) -> Popup.Side:
        """Return the side of the parent window at which popup will appear"""

    def set_side(self, arg: Popup.Side, /) -> None:
        """Set the side of the parent window at which popup will appear"""

    class Side(enum.Enum):
        Left = 0

        Right = 1

    Left: Popup.Side = Popup.Side.Left

    Right: Popup.Side = Popup.Side.Right

class MessageDialog(Window):
    def __init__(self, parent: Widget, type: MessageDialog.Type, title: str = 'Untitled', message: str = 'Message', button_text: str = 'OK', alt_button_text: str = 'Cancel', alt_button: bool = False) -> None: ...

    def message_label(self) -> Label: ...

    def callback(self) -> Callable[[int], None]: ...

    def set_callback(self, arg: Callable[[int], None], /) -> None: ...

    class Type(enum.Enum):
        """Classification of the type of message this MessageDialog represents."""

        Information = 0

        Question = 1

        Warning = 2

class VScrollPanel(Widget):
    def __init__(self, parent: Widget) -> None: ...

    def scroll(self) -> float:
        """
        Return the current scroll amount as a value between 0 and 1. 0 means
        scrolled to the top and 1 to the bottom.
        """

    def set_scroll(self, arg: float, /) -> None:
        """
        Set the scroll amount to a value between 0 and 1. 0 means scrolled to
        the top and 1 to the bottom.
        """

    def scroll_absolute(self, arg: float, /) -> None:
        """Scroll to an absolute pixel position"""

class ComboBox(Widget):
    r"""
    \class ComboBox combobox.h nanogui/combobox.h

    Simple combo box widget based on a popup button.
    """

    @overload
    def __init__(self, parent: Widget) -> None:
        """Create an empty combo box"""

    @overload
    def __init__(self, parent: Widget, items: Sequence[str]) -> None: ...

    @overload
    def __init__(self, parent: Widget, items: Sequence[str], items_short: Sequence[str]) -> None: ...

    def callback(self) -> Callable[[int], None]:
        """The callback to execute for this ComboBox."""

    def set_callback(self, arg: Callable[[int], None], /) -> None:
        """Sets the callback to execute for this ComboBox."""

    def selected_index(self) -> int:
        """The current index this ComboBox has selected."""

    def set_selected_index(self, arg: int, /) -> None:
        """Sets the current index this ComboBox has selected."""

    @overload
    def set_items(self, arg: Sequence[str], /) -> None:
        """
        Sets the items for this ComboBox, providing both short and long
        descriptive lables for each item.
        """

    @overload
    def set_items(self, arg0: Sequence[str], arg1: Sequence[str], /) -> None: ...

    def items(self) -> list[str]:
        """The items associated with this ComboBox."""

    def items_short(self) -> list[str]:
        """The short descriptions associated with this ComboBox."""

class ProgressBar(Widget):
    def __init__(self, parent: Widget) -> None: ...

    def value(self) -> float: ...

    def set_value(self, arg: float, /) -> None: ...

class Slider(Widget):
    def __init__(self, parent: Widget) -> None: ...

    def value(self) -> float: ...

    def set_value(self, arg: float, /) -> None: ...

    def highlight_color(self) -> Color: ...

    def set_highlight_color(self, arg: Color, /) -> None: ...

    def range(self) -> tuple[float, float]: ...

    def set_range(self, arg: tuple[float, float], /) -> None: ...

    def highlighted_range(self) -> tuple[float, float]: ...

    def set_highlighted_range(self, arg: tuple[float, float], /) -> None: ...

    def set_callback(self, arg: Callable[[float], None], /) -> None: ...

    def callback(self) -> Callable[[float], None]: ...

    def set_final_callback(self, arg: Callable[[float], None], /) -> None: ...

    def final_callback(self) -> Callable[[float], None]: ...

class Button(Widget):
    r"""
    \class Button button.h nanogui/button.h

    [Normal/Toggle/Radio/Popup] Button widget.
    """

    def __init__(self, parent: Widget, caption: str = 'Untitled', icon: int = 0) -> None:
        """
        Creates a button attached to the specified parent.

        Parameter ``parent``:
            The nanogui::Widget this Button will be attached to.

        Parameter ``caption``:
            The name of the button (default ``"Untitled"``).

        Parameter ``icon``:
            The icon to display with this Button. See nanogui::Button::mIcon.
        """

    def caption(self) -> str:
        """Returns the caption of this Button."""

    def set_caption(self, arg: str, /) -> None:
        """Sets the caption of this Button."""

    def background_color(self) -> Color:
        """Returns the background color of this Button."""

    def set_background_color(self, arg: Color, /) -> None:
        """Sets the background color of this Button."""

    def text_color(self) -> Color:
        """Returns the text color of the caption of this Button."""

    def set_text_color(self, arg: Color, /) -> None:
        """Sets the text color of the caption of this Button."""

    def icon(self) -> int:
        """Returns the icon of this Button. See nanogui::Button::m_icon."""

    def set_icon(self, arg: int, /) -> None:
        """Sets the icon of this Button. See nanogui::Button::m_icon."""

    def flags(self) -> int:
        """
        The current flags of this Button (see nanogui::Button::Flags for
        options).
        """

    def set_flags(self, arg: int, /) -> None:
        """
        Sets the flags of this Button (see nanogui::Button::Flags for
        options).
        """

    def icon_position(self) -> Button.IconPosition:
        """The position of the icon for this Button."""

    def set_icon_position(self, arg: Button.IconPosition, /) -> None:
        """Sets the position of the icon for this Button."""

    def pushed(self) -> bool:
        """Whether or not this Button is currently pushed."""

    def set_pushed(self, arg: bool, /) -> None:
        """Sets whether or not this Button is currently pushed."""

    def callback(self) -> Callable[[], None]:
        """Return the push callback (for any type of button)"""

    def set_callback(self, arg: Callable[[], None], /) -> None:
        """Set the push callback (for any type of button)."""

    def change_callback(self) -> Callable[[bool], None]:
        """Return the change callback (for toggle buttons)"""

    def set_change_callback(self, arg: Callable[[bool], None], /) -> None:
        """Set the change callback (for toggle buttons)."""

    def button_group(self) -> list[Button]:
        """Return the button group (for radio buttons)"""

    def set_button_group(self, arg: Sequence[Button], /) -> None:
        """Set the button group (for radio buttons)"""

    def padding(self) -> Vector2i:
        """The padding of this Button."""

    def set_padding(self, arg: Vector2i, /) -> None:
        """Set the padding of this Button"""

    class IconPosition(enum.Enum):
        """The available icon positions."""

        Left = 0

        LeftCentered = 1

        RightCentered = 2

        Right = 3

    class Flags(enum.IntFlag):
        """Flags to specify the button behavior (can be combined with binary OR)"""

        NormalButton = 1

        RadioButton = 2

        ToggleButton = 4

        PopupButton = 8

        MenuButton = 16

class ToolButton(Button):
    def __init__(self, parent: Widget, icon: int, caption: str = '') -> None: ...

class PopupButton(Button):
    def __init__(self, parent: Widget, caption: str = 'Untitled', button_icon: int = 0) -> None: ...

    def popup(self) -> Popup: ...

    def chevron_icon(self) -> int: ...

    def set_chevron_icon(self, arg: int, /) -> None: ...

    def side(self) -> Popup.Side: ...

    def set_side(self, arg: Popup.Side, /) -> None: ...

class CheckBox(Widget):
    r"""
    \class CheckBox checkbox.h nanogui/checkbox.h

    Two-state check box widget.

    Remark:
        This class overrides nanogui::Widget::mIconExtraScale to be
        ``1.2f``, which affects all subclasses of this Widget. Subclasses
        must explicitly set a different value if needed (e.g., in their
        constructor).
    """

    @overload
    def __init__(self, parent: Widget, caption: str = 'Untitled') -> None:
        """
        Adds a CheckBox to the specified ``parent``.

        Parameter ``parent``:
            The Widget to add this CheckBox to.

        Parameter ``caption``:
            The caption text of the CheckBox (default ``"Untitled"``).

        Parameter ``callback``:
            If provided, the callback to execute when the CheckBox is checked
            or unchecked. Default parameter function does nothing. See
            nanogui::CheckBox::mPushed for the difference between "pushed" and
            "checked".
        """

    @overload
    def __init__(self, parent: Widget, caption: str, callback: Callable[[bool], None]) -> None: ...

    def caption(self) -> str:
        """The caption of this CheckBox."""

    def set_caption(self, arg: str, /) -> None:
        """Sets the caption of this CheckBox."""

    def checked(self) -> bool:
        """Whether or not this CheckBox is currently checked."""

    def set_checked(self, arg: bool, /) -> None:
        """Sets whether or not this CheckBox is currently checked."""

    def pushed(self) -> bool:
        """
        Whether or not this CheckBox is currently pushed. See
        nanogui::CheckBox::m_pushed.
        """

    def set_pushed(self, arg: bool, /) -> None: ...

    def callback(self) -> Callable[[bool], None]:
        """Returns the current callback of this CheckBox."""

    def set_callback(self, arg: Callable[[bool], None], /) -> None:
        """
        Sets the callback to be executed when this CheckBox is checked /
        unchecked.
        """

class TabWidgetBase(Widget):
    def __init__(self, arg: Widget, /) -> None:
        """Construct a new tab widget"""

    def tab_count(self) -> int:
        """Return the total number of tabs"""

    def tab_id(self, arg: int, /) -> int:
        """Return the ID of the tab at a given index"""

    def tab_index(self, arg: int, /) -> int:
        """Return the index of the tab with a given ID (or throw an exception)"""

    def insert_tab(self, index: int, caption: str) -> int:
        """Inserts a new tab at the specified position and returns its ID."""

    def append_tab(self, caption: str) -> int:
        """Appends a new tab and returns its ID."""

    def remove_tab(self, id: int) -> None:
        """Removes a tab with the specified ID"""

    def selected_index(self) -> int:
        """Return the index of the currently active tab"""

    def set_selected_index(self, id: int) -> None:
        """Set the index of the currently active tab"""

    def selected_id(self) -> int:
        """Return the ID of the currently active tab"""

    def set_selected_id(self, id: int) -> None:
        """Set the ID of the currently active tab"""

    def tab_caption(self, id: int) -> str:
        """Return the caption of the tab with the given ID"""

    def set_tab_caption(self, id: int, caption: str) -> None:
        """Change the caption of the tab with the given ID"""

    def tabs_draggable(self) -> bool:
        """Return whether tabs can be dragged to different positions"""

    def set_tabs_draggable(self, arg: bool, /) -> None: ...

    def tabs_closeable(self) -> bool:
        """Return whether tabs provide a close button"""

    def set_tabs_closeable(self, arg: bool, /) -> None: ...

    def padding(self) -> int:
        """Return the padding between the tab widget boundary and child widgets"""

    def set_padding(self, arg: int, /) -> None: ...

    def set_background_color(self, arg: Color, /) -> None:
        """Set the widget's background color (a global property)"""

    def background_color(self) -> Color:
        """Return the widget's background color (a global property)"""

    def set_callback(self, arg: Callable[[int], None], /) -> None:
        """
        Set a callback that is used to notify a listener about tab changes
        (will be called with the tab ID)
        """

    def callback(self) -> Callable[[int], None]:
        """
        Callback that is used to notify a listener about tab changes (will be
        called with the tab ID)
        """

    def close_callback(self) -> Callable[[int], None]:
        """
        Callback that is used to notify a listener about tab close events
        (will be called with the tab ID)
        """

    def set_close_callback(self, arg: Callable[[int], None], /) -> None:
        """
        Set a callback that is used to notify a listener about tab close
        events (will be called with the tab ID)
        """

    def popup_callback(self) -> Callable[[int, Screen], Popup]:
        """
        Callback that is used to notify a listener about popup events (will be
        called with the tab ID)
        """

    def set_popup_callback(self, arg: Callable[[int, Screen], Popup], /) -> None:
        """
        Set a callback that is used to notify a listener about popup events
        (will be called with the tab ID)
        """

class TabWidget(TabWidgetBase):
    def __init__(self, arg: Widget, /) -> None:
        """Construct a new tab widget"""

    def insert_tab(self, index: int, caption: str, widget: Widget) -> int:
        """Inserts a new tab at the specified position and returns its ID."""

    def append_tab(self, caption: str, widget: Widget) -> int:
        """Appends a new tab and returns its ID."""

    def remove_children(self) -> bool:
        """Remove child widgets when the associated tab is closed/removed?"""

    def set_remove_children(self, id: bool) -> None:
        """Remove child widgets when the associated tab is closed/removed?"""

class TextBox(Widget):
    def __init__(self, parent: Widget, value: str = 'Untitled') -> None: ...

    def editable(self) -> bool: ...

    def set_editable(self, arg: bool, /) -> None: ...

    def spinnable(self) -> bool: ...

    def set_spinnable(self, arg: bool, /) -> None: ...

    def value(self) -> str: ...

    def set_value(self, arg: str, /) -> None: ...

    def default_value(self) -> str: ...

    def set_default_value(self, arg: str, /) -> None: ...

    def alignment(self) -> TextBox.Alignment: ...

    def set_alignment(self, arg: TextBox.Alignment, /) -> None: ...

    def units(self) -> str: ...

    def set_units(self, arg: str, /) -> None: ...

    def units_image(self) -> int: ...

    def set_units_image(self, arg: int, /) -> None: ...

    def format(self) -> str:
        """Return the underlying regular expression specifying valid formats"""

    def set_format(self, arg: str, /) -> None:
        """Specify a regular expression specifying valid formats"""

    def placeholder(self) -> str:
        """
        Return the placeholder text to be displayed while the text box is
        empty.
        """

    def set_placeholder(self, arg: str, /) -> None:
        """
        Specify a placeholder text to be displayed while the text box is
        empty.
        """

    def callback(self) -> Callable[[str], bool]:
        """The callback to execute when the value of this TextBox has changed."""

    def set_callback(self, arg: Callable[[str], bool], /) -> None:
        """
        Sets the callback to execute when the value of this TextBox has
        changed.
        """

    class Alignment(enum.Enum):
        """How to align the text in the text box."""

        Left = 0

        Center = 1

        Right = 2

class IntBox(TextBox):
    r"""
    \class IntBox textbox.h nanogui/textbox.h

    A specialization of TextBox for representing integral values.

    Template parameters should be integral types, e.g. ``int``, ``long``,
    ``uint32_t``, etc.
    """

    def __init__(self, parent: Widget, value: int = 0) -> None: ...

    def value(self) -> int: ...

    def set_value(self, arg: int, /) -> None: ...

    def set_callback(self, arg: Callable[[int], None], /) -> None: ...

    def set_value_increment(self, arg: int, /) -> None: ...

    @overload
    def set_min_value(self, arg: int, /) -> None: ...

    @overload
    def set_min_value(self, arg0: int, arg1: int, /) -> None: ...

    def set_max_value(self, arg: int, /) -> None: ...

class FloatBox(TextBox):
    r"""
    \class FloatBox textbox.h nanogui/textbox.h

    A specialization of TextBox representing floating point values.

    The emplate parametersshould a be floating point type, e.g. ``float``
    or ``double``.
    """

    def __init__(self, parent: Widget, value: float = 0.0) -> None: ...

    def value(self) -> float: ...

    def set_value(self, arg: float, /) -> None: ...

    def set_callback(self, arg: Callable[[float], None], /) -> None: ...

    def set_value_increment(self, arg: float, /) -> None: ...

    @overload
    def set_min_value(self, arg: float, /) -> None: ...

    @overload
    def set_min_value(self, arg0: float, arg1: float, /) -> None: ...

    def set_max_value(self, arg: float, /) -> None: ...

class TextArea(Widget):
    def __init__(self, arg: Widget, /) -> None: ...

    def set_font(self, arg: str, /) -> None:
        """Set the used font"""

    def font(self) -> str:
        """Return the used font"""

    def set_foreground_color(self, arg: Color, /) -> None:
        """Set the foreground color (applies to all subsequently added text)"""

    def foreground_color(self) -> Color:
        """Return the foreground color (applies to all subsequently added text)"""

    def set_background_color(self, arg: Color, /) -> None:
        """Set the widget's background color (a global property)"""

    def background_color(self) -> Color:
        """Return the widget's background color (a global property)"""

    def set_selection_color(self, arg: Color, /) -> None:
        """Set the widget's selection color (a global property)"""

    def selection_color(self) -> Color:
        """Return the widget's selection color (a global property)"""

    def set_padding(self, arg: int, /) -> None:
        """Set the amount of padding to add around the text"""

    def padding(self) -> int:
        """Return the amount of padding that is added around the text"""

    def set_selectable(self, arg: int, /) -> None:
        """Set whether the text can be selected using the mouse"""

    def is_selectable(self) -> int:
        """Return whether the text can be selected using the mouse"""

    def append(self, arg: str, /) -> None:
        """Append text at the end of the widget"""

    def append_line(self, arg: str, /) -> None:
        """Append a line of text at the bottom"""

    def clear(self) -> None:
        """Clear all current contents"""

class Theme(Object):
    def __init__(self, arg: nanovg.NVGcontext, /) -> None: ...

    @property
    def m_font_sans_regular(self) -> int:
        """
        The standard font face (default: ``"sans"`` from
        ``resources/roboto_regular.ttf``).
        """

    @m_font_sans_regular.setter
    def m_font_sans_regular(self, arg: int, /) -> None: ...

    @property
    def m_font_sans_bold(self) -> int:
        """
        The bold font face (default: ``"sans-bold"`` from
        ``resources/roboto_regular.ttf``).
        """

    @m_font_sans_bold.setter
    def m_font_sans_bold(self, arg: int, /) -> None: ...

    @property
    def m_font_icons(self) -> int:
        """
        The icon font face (default: ``"icons"`` from
        ``resources/entypo.ttf``).
        """

    @m_font_icons.setter
    def m_font_icons(self, arg: int, /) -> None: ...

    @property
    def m_font_mono_regular(self) -> int:
        """
        The monospace font face (default: ``"mono"`` from
        ``resources/inconsolata_regular.ttf``).
        """

    @m_font_mono_regular.setter
    def m_font_mono_regular(self, arg: int, /) -> None: ...

    @property
    def m_icon_scale(self) -> float:
        """
        The amount of scaling that is applied to each icon to fit the size of
        NanoGUI widgets. The default value is ``0.77f``, setting to e.g.
        higher than ``1.0f`` is generally discouraged.
        """

    @m_icon_scale.setter
    def m_icon_scale(self, arg: float, /) -> None: ...

    @property
    def m_standard_font_size(self) -> int:
        """
        The font size for all widgets other than buttons and textboxes
        (default: `` 16``).
        """

    @m_standard_font_size.setter
    def m_standard_font_size(self, arg: int, /) -> None: ...

    @property
    def m_button_font_size(self) -> int:
        """The font size for buttons (default: ``20``)."""

    @m_button_font_size.setter
    def m_button_font_size(self, arg: int, /) -> None: ...

    @property
    def m_text_box_font_size(self) -> int:
        """The font size for text boxes (default: ``20``)."""

    @m_text_box_font_size.setter
    def m_text_box_font_size(self, arg: int, /) -> None: ...

    @property
    def m_window_corner_radius(self) -> int:
        """Rounding radius for Window widget corners (default: ``2``)."""

    @m_window_corner_radius.setter
    def m_window_corner_radius(self, arg: int, /) -> None: ...

    @property
    def m_window_header_height(self) -> int:
        """Default size of Window widget titles (default: ``30``)."""

    @m_window_header_height.setter
    def m_window_header_height(self, arg: int, /) -> None: ...

    @property
    def m_window_drop_shadow_size(self) -> int:
        """
        Size of drop shadow rendered behind the Window widgets (default:
        ``10``).
        """

    @m_window_drop_shadow_size.setter
    def m_window_drop_shadow_size(self, arg: int, /) -> None: ...

    @property
    def m_button_corner_radius(self) -> int:
        """
        Rounding radius for Button (and derived types) widgets (default:
        ``2``).
        """

    @m_button_corner_radius.setter
    def m_button_corner_radius(self, arg: int, /) -> None: ...

    @property
    def m_tab_border_width(self) -> float:
        """The border width for Tab_header widgets (default: ``0.75f``)."""

    @m_tab_border_width.setter
    def m_tab_border_width(self, arg: float, /) -> None: ...

    @property
    def m_tab_inner_margin(self) -> int:
        """The inner margin on a Tab_header widget (default: ``5``)."""

    @m_tab_inner_margin.setter
    def m_tab_inner_margin(self, arg: int, /) -> None: ...

    @property
    def m_tab_min_button_width(self) -> int:
        """The minimum size for buttons on a Tab_header widget (default: ``20``)."""

    @m_tab_min_button_width.setter
    def m_tab_min_button_width(self, arg: int, /) -> None: ...

    @property
    def m_tab_max_button_width(self) -> int:
        """
        The maximum size for buttons on a Tab_header widget (default:
        ``160``).
        """

    @m_tab_max_button_width.setter
    def m_tab_max_button_width(self, arg: int, /) -> None: ...

    @property
    def m_tab_control_width(self) -> int:
        """
        Used to help specify what lies "in bound" for a Tab_header widget
        (default: ``20``).
        """

    @m_tab_control_width.setter
    def m_tab_control_width(self, arg: int, /) -> None: ...

    @property
    def m_tab_button_horizontal_padding(self) -> int:
        """
        The amount of horizontal padding for a Tab_header widget (default:
        ``10``).
        """

    @m_tab_button_horizontal_padding.setter
    def m_tab_button_horizontal_padding(self, arg: int, /) -> None: ...

    @property
    def m_tab_button_vertical_padding(self) -> int:
        """
        The amount of vertical padding for a Tab_header widget (default:
        ``2``).
        """

    @m_tab_button_vertical_padding.setter
    def m_tab_button_vertical_padding(self, arg: int, /) -> None: ...

    @property
    def m_drop_shadow(self) -> Color:
        """
        The color of the drop shadow drawn behind widgets (default:
        intensity=``0``, alpha=``128``; see nanogui::Color::Color(int,int)).
        """

    @m_drop_shadow.setter
    def m_drop_shadow(self, arg: Color, /) -> None: ...

    @property
    def m_transparent(self) -> Color:
        """
        The transparency color (default: intensity=``0``, alpha=``0``; see
        nanogui::Color::Color(int,int)).
        """

    @m_transparent.setter
    def m_transparent(self, arg: Color, /) -> None: ...

    @property
    def m_border_dark(self) -> Color:
        """
        The dark border color (default: intensity=``29``, alpha=``255``; see
        nanogui::Color::Color(int,int)).
        """

    @m_border_dark.setter
    def m_border_dark(self, arg: Color, /) -> None: ...

    @property
    def m_border_light(self) -> Color:
        """
        The light border color (default: intensity=``92``, alpha=``255``; see
        nanogui::Color::Color(int,int)).
        """

    @m_border_light.setter
    def m_border_light(self, arg: Color, /) -> None: ...

    @property
    def m_border_medium(self) -> Color:
        """
        The medium border color (default: intensity=``35``, alpha=``255``; see
        nanogui::Color::Color(int,int)).
        """

    @m_border_medium.setter
    def m_border_medium(self, arg: Color, /) -> None: ...

    @property
    def m_text_color(self) -> Color:
        """
        The text color (default: intensity=``255``, alpha=``160``; see
        nanogui::Color::Color(int,int)).
        """

    @m_text_color.setter
    def m_text_color(self, arg: Color, /) -> None: ...

    @property
    def m_disabled_text_color(self) -> Color:
        """
        The disable dtext color (default: intensity=``255``, alpha=``80``; see
        nanogui::Color::Color(int,int)).
        """

    @m_disabled_text_color.setter
    def m_disabled_text_color(self, arg: Color, /) -> None: ...

    @property
    def m_text_color_shadow(self) -> Color:
        """
        The text shadow color (default: intensity=``0``, alpha=``160``; see
        nanogui::Color::Color(int,int)).
        """

    @m_text_color_shadow.setter
    def m_text_color_shadow(self, arg: Color, /) -> None: ...

    @property
    def m_icon_color(self) -> Color:
        """The icon color (default: nanogui::Theme::m_text_color)."""

    @m_icon_color.setter
    def m_icon_color(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_top_focused(self) -> Color:
        """
        The top gradient color for buttons in focus (default:
        intensity=``64``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_top_focused.setter
    def m_button_gradient_top_focused(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_bot_focused(self) -> Color:
        """
        The bottom gradient color for buttons in focus (default:
        intensity=``48``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_bot_focused.setter
    def m_button_gradient_bot_focused(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_top_unfocused(self) -> Color:
        """
        The top gradient color for buttons not in focus (default:
        intensity=``74``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_top_unfocused.setter
    def m_button_gradient_top_unfocused(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_bot_unfocused(self) -> Color:
        """
        The bottom gradient color for buttons not in focus (default:
        intensity=``58``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_bot_unfocused.setter
    def m_button_gradient_bot_unfocused(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_top_pushed(self) -> Color:
        """
        The top gradient color for buttons currently pushed (default:
        intensity=``41``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_top_pushed.setter
    def m_button_gradient_top_pushed(self, arg: Color, /) -> None: ...

    @property
    def m_button_gradient_bot_pushed(self) -> Color:
        """
        The bottom gradient color for buttons currently pushed (default:
        intensity=``29``, alpha=``255``; see nanogui::Color::Color(int,int)).
        """

    @m_button_gradient_bot_pushed.setter
    def m_button_gradient_bot_pushed(self, arg: Color, /) -> None: ...

    @property
    def m_window_fill_unfocused(self) -> Color:
        """
        The fill color for a Window that is not in focus (default:
        intensity=``43``, alpha=``230``; see nanogui::Color::Color(int,int)).
        """

    @m_window_fill_unfocused.setter
    def m_window_fill_unfocused(self, arg: Color, /) -> None: ...

    @property
    def m_window_fill_focused(self) -> Color:
        """
        The fill color for a Window that is in focus (default:
        intensity=``45``, alpha=``230``; see nanogui::Color::Color(int,int)).
        """

    @m_window_fill_focused.setter
    def m_window_fill_focused(self, arg: Color, /) -> None: ...

    @property
    def m_window_title_unfocused(self) -> Color:
        """
        The title color for a Window that is not in focus (default:
        intensity=``220``, alpha=``160``; see nanogui::Color::Color(int,int)).
        """

    @m_window_title_unfocused.setter
    def m_window_title_unfocused(self, arg: Color, /) -> None: ...

    @property
    def m_window_title_focused(self) -> Color:
        """
        The title color for a Window that is in focus (default:
        intensity=``255``, alpha=``190``; see nanogui::Color::Color(int,int)).
        """

    @m_window_title_focused.setter
    def m_window_title_focused(self, arg: Color, /) -> None: ...

    @property
    def m_window_header_gradient_top(self) -> Color:
        """
        The top gradient color for Window headings (default:
        nanogui::Theme::m_button_gradient_top_unfocused).
        """

    @m_window_header_gradient_top.setter
    def m_window_header_gradient_top(self, arg: Color, /) -> None: ...

    @property
    def m_window_header_gradient_bot(self) -> Color:
        """
        The bottom gradient color for Window headings (default:
        nanogui::Theme::m_button_gradient_bot_unfocused).
        """

    @m_window_header_gradient_bot.setter
    def m_window_header_gradient_bot(self, arg: Color, /) -> None: ...

    @property
    def m_window_header_sep_top(self) -> Color:
        """
        The Window header top separation color (default:
        nanogui::Theme::m_border_light).
        """

    @m_window_header_sep_top.setter
    def m_window_header_sep_top(self, arg: Color, /) -> None: ...

    @property
    def m_window_header_sep_bot(self) -> Color:
        """
        The Window header bottom separation color (default:
        nanogui::Theme::m_border_dark).
        """

    @m_window_header_sep_bot.setter
    def m_window_header_sep_bot(self, arg: Color, /) -> None: ...

    @property
    def m_window_popup(self) -> Color:
        """
        The popup window color (default: intensity=``50``, alpha=``255``; see
        nanogui::Color::Color(int,int))).
        """

    @m_window_popup.setter
    def m_window_popup(self, arg: Color, /) -> None: ...

    @property
    def m_window_popup_transparent(self) -> Color:
        """
        The transparent popup window color (default: intensity=``50``,
        alpha=``0``; see nanogui::Color::Color(int,int))).
        """

    @m_window_popup_transparent.setter
    def m_window_popup_transparent(self, arg: Color, /) -> None: ...

    @property
    def m_check_box_icon(self) -> int:
        """Icon to use for check box widgets (default: ``FA_CHECK``)."""

    @m_check_box_icon.setter
    def m_check_box_icon(self, arg: int, /) -> None: ...

    @property
    def m_message_information_icon(self) -> int:
        """
        Icon to use for informational message dialog widgets (default:
        ``FA_INFO_CIRCLE``).
        """

    @m_message_information_icon.setter
    def m_message_information_icon(self, arg: int, /) -> None: ...

    @property
    def m_message_question_icon(self) -> int:
        """
        Icon to use for interrogative message dialog widgets (default:
        ``FA_QUESTION_CIRCLE``).
        """

    @m_message_question_icon.setter
    def m_message_question_icon(self, arg: int, /) -> None: ...

    @property
    def m_message_warning_icon(self) -> int:
        """
        Icon to use for warning message dialog widgets (default:
        ``FA_EXCLAMATION_TRINAGLE``).
        """

    @m_message_warning_icon.setter
    def m_message_warning_icon(self, arg: int, /) -> None: ...

    @property
    def m_message_alt_button_icon(self) -> int:
        """
        Icon to use on message dialog alt button (default:
        ``FA_CIRCLE_WITH_CROSS``).
        """

    @m_message_alt_button_icon.setter
    def m_message_alt_button_icon(self, arg: int, /) -> None: ...

    @property
    def m_message_primary_button_icon(self) -> int:
        """Icon to use on message_dialog primary button (default: ``FA_CHECK``)."""

    @m_message_primary_button_icon.setter
    def m_message_primary_button_icon(self, arg: int, /) -> None: ...

    @property
    def m_popup_chevron_right_icon(self) -> int:
        """
        Icon to use for Popup_button widgets opening to the right (default:
        ``FA_CHEVRON_RIGHT``).
        """

    @m_popup_chevron_right_icon.setter
    def m_popup_chevron_right_icon(self, arg: int, /) -> None: ...

    @property
    def m_popup_chevron_left_icon(self) -> int:
        """
        Icon to use for Popup_button widgets opening to the left (default:
        ``FA_CHEVRON_LEFT``).
        """

    @m_popup_chevron_left_icon.setter
    def m_popup_chevron_left_icon(self, arg: int, /) -> None: ...

    @property
    def m_text_box_up_icon(self) -> int:
        """
        Icon to use when a text box has an up toggle (e.g. IntBox) (default:
        ``FA_CHEVRON_UP``).
        """

    @m_text_box_up_icon.setter
    def m_text_box_up_icon(self, arg: int, /) -> None: ...

    @property
    def m_text_box_down_icon(self) -> int:
        """
        Icon to use when a text box has a down toggle (e.g. IntBox) (default:
        ``FA_CHEVRON_DOWN``).
        """

    @m_text_box_down_icon.setter
    def m_text_box_down_icon(self, arg: int, /) -> None: ...

class Canvas(Widget):
    r"""
    \class GLCanvas canvas.h nanogui/canvas.h

    Canvas widget for rendering OpenGL/GLES2/Metal content

    Canvas widget that can be used to display arbitrary OpenGL content.
    This is useful to display and manipulate 3D objects as part of an
    interactive application. The implementation uses scissoring to ensure
    that rendered objects don't spill into neighboring widgets.

    \rst **Usage** Override :func:`nanogui::GLCanvas::draw_contents` in
    subclasses to provide custom drawing code. See
    :ref:`nanogui_example_4`.

    \endrst
    """

    def __init__(self, parent: Widget, samples: int = 4, has_depth_buffer: bool = True, has_stencil_buffer: bool = False, clear: bool = True) -> None:
        """
        Creates a new Canvas widget

        Parameter ``parent``:
            The parent widget

        Parameter ``samples``:
            The number of pixel samples (MSAA)

        Parameter ``has_depth_buffer``:
            Should the widget allocate a depth buffer for the underlying
            render pass?

        Parameter ``has_stencil_buffer``:
            Should the widget allocate a stencil buffer for the underlying
            render pass?

        Parameter ``clear``:
            Should the widget clear its color/depth/stencil buffer?
        """

    def render_pass(self) -> RenderPass:
        """Return the render pass associated with the canvas object"""

    def draw_border(self) -> bool:
        """Return whether the widget border will be drawn"""

    def set_draw_border(self, arg: bool, /) -> None:
        """Specify whether to draw the widget border"""

    def border_color(self) -> Color:
        """Return whether the widget border is drawn"""

    def set_border_color(self, arg: Color, /) -> None:
        """Specify the widget border color"""

    def background_color(self) -> Color:
        """Return whether the widget border is drawn"""

    def set_background_color(self, arg: Color, /) -> None:
        """Specify the widget background color"""

    def draw_contents(self) -> None:
        """Draw the widget contents. Override this method."""

class ImageView(Canvas):
    def __init__(self, arg: Widget, /) -> None:
        """Initialize the widget"""

    def image(self) -> Texture:
        """Return the currently active image"""

    def set_image(self, arg: Texture, /) -> None:
        """Set the currently active image"""

    def reset(self) -> None:
        """Center the image on the screen and set the scale to 1:1"""

    def center(self) -> None:
        """Center the image on the screen"""

    def offset(self) -> Vector2f:
        """Return the pixel offset of the zoomed image rectangle"""

    def set_offset(self, arg: Vector2f, /) -> None:
        """Set the pixel offset of the zoomed image rectangle"""

    def scale(self) -> float:
        """Return the current magnification of the image"""

    def set_scale(self, arg: float, /) -> None:
        """Set the current magnification of the image"""

    def pos_to_pixel(self, arg: Vector2f, /) -> Vector2f:
        """Convert a position within the widget to a pixel position in the image"""

    def pixel_to_pos(self, arg: Vector2f, /) -> Vector2f:
        """Convert a pixel position in the image to a position within the widget"""

    def set_pixel_callback(self, arg: Callable[[Vector2i], Sequence[str]], /) -> None:
        """
        Set the callback that is used to acquire information about pixel
        components
        """

class FormHelper:
    r"""
    \class FormHelper formhelper.h nanogui/formhelper.h

    Convenience class to create simple AntTweakBar-style layouts that
    expose variables of various types using NanoGUI widgets

    **Example**:

    \rst .. code-block:: cpp

    // [ ... initialize NanoGUI, construct screen ... ]

    FormHelper* h = new FormHelper(screen);

    // Add a new windows widget h->add_window(Vector2i(10,10),"Menu");

    // Start a new group h->add_group("Group 1");

    // Expose an integer variable by reference h->add_variable("integer
    variable", a_int);

    // Expose a float variable via setter/getter functions
    h->add_variable( [&](float value) { a_float = value; }, [&]() { return
    *a_float; }, "float variable");

    // add a new button h->add_button("Button", [&]() { std::cout <<
    "Button pressed" << std::endl; });

    \endrst
    """

    def __init__(self, arg: Screen, /) -> None:
        """Create a helper class to construct NanoGUI widgets on the given screen"""

    def add_window(self, pos: Vector2i, title: str = 'Untitled') -> Window:
        """Add a new top-level window"""

    def add_group(self, arg: str, /) -> Label:
        """Add a new group that may contain several sub-widgets"""

    def add_button(self, label: str, cb: Callable[[], None]) -> Button:
        """Add a new group that may contain several sub-widgets"""

    def add_bool_variable(self, label: str, setter: Callable[[bool], None], getter: Callable[[], bool], editable: bool = True) -> CheckBox: ...

    def add_int_variable(self, label: str, setter: Callable[[int], None], getter: Callable[[], int], editable: bool = True) -> IntBox: ...

    def add_double_variable(self, label: str, setter: Callable[[float], None], getter: Callable[[], float], editable: bool = True) -> FloatBox: ...

    def add_string_variable(self, label: str, setter: Callable[[str], None], getter: Callable[[], str], editable: bool = True) -> TextBox: ...

    def add_color_variable(self, label: str, setter: Callable[[Color], None], getter: Callable[[], Color], editable: bool = True) -> ColorPicker: ...

    def add_enum_variable(self, label: str, setter: Callable[[int], None], getter: Callable[[], int], editable: bool = True) -> ComboBox: ...

    def add_widget(self, arg0: str, arg1: Widget, /) -> None:
        """Add an arbitrary (optionally labeled) widget to the layout"""

    def refresh(self) -> None:
        """Cause all widgets to re-synchronize with the underlying variable state"""

    def window(self) -> Window:
        """Access the currently active Window instance"""

    def set_window(self, arg: Window, /) -> None:
        """Set the active Window instance."""

    def fixed_size(self) -> Vector2i:
        """The current fixed size being used for newly added widgets."""

    def set_fixed_size(self, arg: Vector2i, /) -> None:
        """Specify a fixed size for newly added widgets"""

    def group_font_name(self) -> str:
        """The font name being used for group headers."""

    def set_group_font_name(self, arg: str, /) -> None:
        """Sets the font name to be used for group headers."""

    def label_font_name(self) -> str:
        """The font name being used for labels."""

    def set_label_font_name(self, arg: str, /) -> None:
        """Sets the font name being used for labels."""

    def group_font_size(self) -> int:
        """The size of the font being used for group headers."""

    def set_group_font_size(self, arg: int, /) -> None:
        """Sets the size of the font being used for group headers."""

    def label_font_size(self) -> int:
        """The size of the font being used for labels."""

    def set_label_font_size(self, arg: int, /) -> None:
        """Sets the size of the font being used for labels."""

    def widget_font_size(self) -> int:
        """The size of the font being used for non-group / non-label widgets."""

    def set_widget_font_size(self, arg: int, /) -> None:
        """
        Sets the size of the font being used for non-group / non-label
        widgets.
        """

class ColorWheel(Widget):
    r"""
    \class ColorWheel colorwheel.h nanogui/colorwheel.h

    Fancy analog widget to select a color value. This widget was
    contributed by Dmitriy Morozov.
    """

    @overload
    def __init__(self, parent: Widget) -> None:
        """
        Adds a ColorWheel to the specified parent.

        Parameter ``parent``:
            The Widget to add this ColorWheel to.

        Parameter ``color``:
            The initial color of the ColorWheel (default: Red).
        """

    @overload
    def __init__(self, parent: Widget, Color: Color) -> None: ...

    def color(self) -> Color:
        """The current Color this ColorWheel has selected."""

    def set_color(self, arg: Color, /) -> None:
        """Sets the current Color this ColorWheel has selected."""

    def callback(self) -> Callable[[Color], None]:
        """The callback to execute when a user changes the ColorWheel value."""

    def set_callback(self, arg: Callable[[Color], None], /) -> None:
        """Sets the callback to execute when a user changes the ColorWheel value."""

class ColorPicker(PopupButton):
    r"""
    \class ColorPicker colorpicker.h nanogui/colorpicker.h

    Push button with a popup to tweak a color value.
    """

    @overload
    def __init__(self, parent: Widget) -> None:
        """
        Attaches a ColorPicker to the specified parent.

        Parameter ``parent``:
            The Widget to add this ColorPicker to.

        Parameter ``color``:
            The color initially selected by this ColorPicker (default: Red).
        """

    @overload
    def __init__(self, parent: Widget, Color: Color) -> None: ...

    def color(self) -> Color:
        """Get the current color"""

    def set_color(self, arg: Color, /) -> None:
        """Set the current color"""

    def callback(self) -> Callable[[Color], None]:
        """The callback executed when the ColorWheel changes."""

    def set_callback(self, arg: Callable[[Color], None], /) -> None:
        """
        Sets the callback is executed as the ColorWheel itself is changed. Set
        this callback if you need to receive updates for the ColorWheel
        changing before the user clicks nanogui::ColorPicker::mPickButton or
        nanogui::ColorPicker::mPickButton.
        """

    def final_callback(self) -> Callable[[Color], None]:
        """
        The callback to execute when a new Color is selected on the ColorWheel
        **and** the user clicks the nanogui::ColorPicker::m_pick_button or
        nanogui::ColorPicker::m_reset_button.
        """

    def set_final_callback(self, arg: Callable[[Color], None], /) -> None:
        """
        The callback to execute when a new Color is selected on the ColorWheel
        **and** the user clicks the nanogui::ColorPicker::m_pick_button or
        nanogui::ColorPicker::m_reset_button.
        """

class Graph(Widget):
    r"""
    \class Graph graph.h nanogui/graph.h

    Simple graph widget for showing a function plot.
    """

    def __init__(self, parent: Widget, caption: str = 'Untitled') -> None: ...

    def caption(self) -> str: ...

    def set_caption(self, arg: str, /) -> None: ...

    def header(self) -> str: ...

    def set_header(self, arg: str, /) -> None: ...

    def footer(self) -> str: ...

    def set_footer(self, arg: str, /) -> None: ...

    def background_color(self) -> Color: ...

    def set_background_color(self, arg: Color, /) -> None: ...

    def fill_color(self) -> Color: ...

    def set_fill_color(self, arg: Color, /) -> None: ...

    def stroke_color(self) -> Color: ...

    def set_stroke_color(self, arg: Color, /) -> None: ...

    def text_color(self) -> Color: ...

    def set_text_color(self, arg: Color, /) -> None: ...

    def values(self) -> list[float]: ...

    def set_values(self, arg: Sequence[float], /) -> None: ...

class ImagePanel(Widget):
    def __init__(self, parent: Widget) -> None: ...

    def images(self) -> list[tuple[int, str]]: ...

    def set_images(self, arg: Sequence[tuple[int, str]], /) -> None: ...

    def callback(self) -> Callable[[int], None]: ...

    def set_callback(self, arg: Callable[[int], None], /) -> None: ...

class Texture(Object):
    @overload
    def __init__(self, pixel_format: Texture.PixelFormat, component_format: Texture.ComponentFormat, size: Vector2i, min_interpolation_mode: Texture.InterpolationMode = Texture.InterpolationMode.Bilinear, mag_interpolation_mode: Texture.InterpolationMode = Texture.InterpolationMode.Bilinear, wrap_mode: Texture.WrapMode = Texture.WrapMode.ClampToEdge, samples: int = 1, flags: int = 1, mipmap_manual: bool = False) -> None:
        r"""
        Allocate memory for a texture with the given configuration

        \note Certain combinations of pixel and component formats may not be
        natively supported by the hardware. In this case, init() chooses a
        similar supported configuration that can subsequently be queried using
        pixel_format() and component_format(). Some caution must be exercised
        in this case, since upload() will need to provide the data in a
        different storage format.
        """

    @overload
    def __init__(self, filename: str, min_interpolation_mode: Texture.InterpolationMode = Texture.InterpolationMode.Bilinear, mag_interpolation_mode: Texture.InterpolationMode = Texture.InterpolationMode.Bilinear, wrap_mode: Texture.WrapMode = Texture.WrapMode.ClampToEdge) -> None:
        """Load an image from the given file using stb-image"""

    class PixelFormat(enum.Enum):
        """Overall format of the texture (e.g. luminance-only or RGBA)"""

        R = 0
        """Single-channel bitmap"""

        RA = 1
        """Two-channel bitmap"""

        RGB = 2
        """RGB bitmap"""

        RGBA = 3
        """RGB bitmap + alpha channel"""

        BGR = 4
        """BGR bitmap"""

        BGRA = 5
        """BGR bitmap + alpha channel"""

        Depth = 6
        """Depth map"""

        DepthStencil = 7
        """Combined depth + stencil map"""

    class ComponentFormat(enum.Enum):
        """Number format of pixel components"""

        UInt8 = 2

        Int8 = 1

        UInt16 = 4

        Int16 = 3

        UInt32 = 6

        Int32 = 5

        Float16 = 9

        Float32 = 10

    class InterpolationMode(enum.Enum):
        """Texture interpolation mode"""

        Nearest = 0
        """Nearest neighbor interpolation"""

        Bilinear = 1
        """Bilinear ineterpolation"""

        Trilinear = 2
        """Trilinear interpolation (using MIP mapping)"""

    class WrapMode(enum.Enum):
        """How should out-of-bounds texture evaluations be handled?"""

        ClampToEdge = 0
        """Clamp evaluations to the edge of the texture"""

        Repeat = 1
        """Repeat the texture"""

        MirrorRepeat = 2
        """Repeat, but flip the texture after crossing the boundary"""

    class TextureFlags(enum.IntEnum):
        """How will the texture be used? (Must specify at least one)"""

        ShaderRead = 1
        """Texture to be read in shaders"""

        RenderTarget = 2
        """Target framebuffer for rendering"""

    def pixel_format(self) -> Texture.PixelFormat:
        """Return the pixel format"""

    def component_format(self) -> Texture.ComponentFormat:
        """Return the component format"""

    def min_interpolation_mode(self) -> Texture.InterpolationMode:
        """Return the interpolation mode for minimization"""

    def mag_interpolation_mode(self) -> Texture.InterpolationMode:
        """Return the interpolation mode for minimization"""

    def wrap_mode(self) -> Texture.WrapMode:
        """Return the wrap mode"""

    def samples(self) -> int:
        """Return the number of samples (MSAA)"""

    def flags(self) -> int:
        """Return a combination of flags (from Texture::TextureFlags)"""

    def size(self) -> Vector2i:
        """Return the size of this texture"""

    def bytes_per_pixel(self) -> int:
        """Return the number of bytes consumed per pixel of this texture"""

    def channels(self) -> int:
        """Return the number of channels of this texture"""

    def download(self) -> NDArray:
        """Download packed pixel data from the GPU to the CPU"""

    @overload
    def upload(self, arg: Annotated[NDArray, dict(order='C', device='cpu')], /) -> None:
        """Upload packed pixel data from the CPU to the GPU"""

    @overload
    def upload(self, : Optional[object]) -> None: ...

    def upload_async(self, arg: Annotated[NDArray, dict(order='C', device='cpu')], /) -> None:
        """Upload packed pixel data from the CPU to the GPU"""

    def upload_sub_region(self, arg0: Annotated[NDArray, dict(order='C', device='cpu')], arg1: Vector2i, /) -> None:
        """
        Upload packed pixel data to a rectangular sub-region of the texture from the CPU to the GPU
        """

    def generate_mipmap(self) -> None:
        """
        Generates the mipmap. Done automatically upon upload if manual mipmapping is disabled
        """

    def resize(self, arg: Vector2i, /) -> None:
        """Resize the texture (discards the current contents)"""

    def texture_handle(self) -> int: ...

    def renderbuffer_handle(self) -> int: ...

class Shader(Object):
    def __init__(self, render_pass: RenderPass, name: str, vertex_shader: str, fragment_shader: str, blend_mode: Shader.BlendMode = Shader.BlendMode.None) -> None:
        """
        Initialize the shader using the specified source strings.

        Parameter ``render_pass``:
            RenderPass object encoding targets to which color, depth, and
            stencil information will be rendered.

        Parameter ``name``:
            A name identifying this shader

        Parameter ``vertex_shader``:
            The source of the vertex shader as a string.

        Parameter ``fragment_shader``:
            The source of the fragment shader as a string.
        """

    class BlendMode(enum.Enum):
        """Alpha blending mode"""

        None = 0

        AlphaBlend = 1

    def name(self) -> str:
        """Return the name of this shader"""

    def blend_mode(self) -> Shader.BlendMode:
        """Return the blending mode of this shader"""

    def set_buffer(self, arg0: str, arg1: Annotated[NDArray, dict(order='C', device='cpu')], /) -> None:
        """
        Upload a buffer (e.g. vertex positions) that will be associated with a
        named shader parameter.

        Note that this function should be used both for 'varying' and
        'uniform' data---the implementation takes care of routing the data to
        the right endpoint. Matrices should be specified in column-major
        order.

        The buffer will be replaced if it is already present.
        """

    def set_texture(self, arg0: str, arg1: Texture, /) -> None:
        """
        Associate a texture with a named shader parameter

        The association will be replaced if it is already present.
        """

    def begin(self) -> None:
        """
        Begin drawing using this shader

        Note that any updates to 'uniform' and 'varying' shader parameters
        *must* occur prior to this method call.

        The Python bindings also include extra ``__enter__`` and ``__exit__``
        aliases so that the shader can be activated via Pythons 'with'
        statement.
        """

    def end(self) -> None:
        """End drawing using this shader"""

    def __enter__(self) -> None: ...

    def __exit__(self, type: Optional[object], value: Optional[object], traceback: Optional[object]) -> None: ...

    def draw_array(self, primitive_type: Shader.PrimitiveType, offset: int, count: int, indexed: bool = False) -> None:
        """
        Render geometry arrays, either directly or using an index array.

        Parameter ``primitive_type``:
            What type of geometry should be rendered?

        Parameter ``offset``:
            First index to render. Must be a multiple of 2 or 3 for lines and
            triangles, respectively (unless specified using strips).

        Parameter ``offset``:
            Number of indices to render. Must be a multiple of 2 or 3 for
            lines and triangles, respectively (unless specified using strips).

        Parameter ``indexed``:
            Render indexed geometry? In this case, an ``uint32_t`` valued
            buffer with name ``indices`` must have been uploaded using set().
        """

    def shader_handle(self) -> int: ...

    def vertex_array_handle(self) -> int: ...

    class PrimitiveType(enum.Enum):
        """The type of geometry that should be rendered"""

        Point = 0

        Line = 1

        LineStrip = 2

        Triangle = 3

        TriangleStrip = 4

class RenderPass(Object):
    def __init__(self, color_targets: Sequence[Object], depth_target: Optional[Object] = None, stencil_target: Optional[Object] = None, blit_target: Optional[Object] = None, clear: bool = True) -> None:
        """
        Create a new render pass for rendering to a specific set of targets

        Parameter ``color_targets``:
            One or more target objects to which color information will be
            rendered. Must either be a Screen or a Texture instance.

        Parameter ``depth_target``:
            Target object to which depth information will be rendered. Must
            either be ``NULL`` or a Texture instance.

        Parameter ``stencil_target``:
            Target object to which stencil information will be rendered. Must
            either be ``NULL`` or a Texture instance. Can be identical to
            'depth_target' in case the texture has the pixel format
            Texture::PixelFormat::DepthStencil.

        Parameter ``blit_target``:
            When rendering finishes, the render pass can (optionally) blit the
            framebuffer to another target (which can either be another
            RenderPass instance or a Screen instance). This is mainly useful
            for multisample antialiasing (MSAA) rendering where set of multi-
            sample framebuffers must be converted into ordinary framebuffers
            for display.

        Parameter ``clear``:
            Should enter() begin by clearing all buffers?
        """

    def set_clear_color(self, arg0: int, arg1: Color, /) -> None:
        """Set the clear color for a given color attachment"""

    def clear_color(self, arg: int, /) -> Color:
        """Return the clear color for a given color attachment"""

    def set_clear_depth(self, arg: float, /) -> None:
        """Set the clear depth for the depth attachment"""

    def clear_depth(self) -> float:
        """Return the clear depth for the depth attachment"""

    def set_clear_stencil(self, arg: int, /) -> None:
        """Set the clear stencil for the stencil attachment"""

    def clear_stencil(self) -> int:
        """Return the clear stencil for the stencil attachment"""

    def set_viewport(self, offset: Vector2i, size: Vector2i) -> None:
        """Set the pixel offset and size of the viewport region"""

    def viewport(self) -> tuple[Vector2i, Vector2i]:
        """Return the pixel offset and size of the viewport region"""

    def set_depth_test(self, depth_test: RenderPass.DepthTest, depth_write: bool) -> None:
        """Specify the depth test and depth write mask of this render pass"""

    def depth_test(self) -> tuple[RenderPass.DepthTest, bool]:
        """Return the depth test and depth write mask of this render pass"""

    def set_cull_mode(self, arg: RenderPass.CullMode, /) -> None:
        """Specify the culling mode associated with the render pass"""

    def cull_mode(self) -> RenderPass.CullMode:
        """Return the culling mode associated with the render pass"""

    def begin(self) -> None:
        """
        Begin the render pass

        The specified drawing state (e.g. depth tests, culling mode, blending
        mode) are automatically set up at this point. Later changes between
        begin() and end() are possible but cause additional OpenGL/GLES/Metal
        API calls.

        The Python bindings also include extra ``__enter__`` and ``__exit__``
        aliases so that the render pass can be activated via Pythons 'with'
        statement.
        """

    def end(self) -> None:
        """Finish the render pass"""

    def resize(self, arg: Vector2i, /) -> None:
        """Resize all texture targets attached to the render pass"""

    def blit_to(self, src_offset: Vector2i, src_size: Vector2i, dst: Object, dst_offset: Vector2i) -> None:
        """
        Blit the framebuffer to another target (which can either be another
        RenderPass instance or a Screen instance).
        """

    def __enter__(self) -> None: ...

    def __exit__(self, type: Optional[object], value: Optional[object], traceback: Optional[object]) -> None: ...

    def framebuffer_handle(self) -> int: ...

    class CullMode(enum.Enum):
        """Culling mode"""

        Disabled = 0

        Front = 1

        Back = 2

    class DepthTest(enum.Enum):
        """Depth test"""

        Never = 0

        Less = 1

        Equal = 2

        LessEqual = 3

        Greater = 4

        NotEqual = 5

        GreaterEqual = 6

        Always = 7

class TexturedQuad(Shader):
    """
    Textured quad

    This convenience class implements a shader that renders a textured quad
    on the supported platforms (OpenGL, EGL, Metal)
    """

    def __init__(self, render_pass: RenderPass, blend_mode: Shader.BlendMode = Shader.BlendMode.None) -> None:
        """
        Initialize the quad renderer

        Parameter ``render_pass``:
            RenderPass object encoding targets to which the quad will be rendered

        Parameter ``blend_mode``:
            Alpha blending mode for rendering
        """

    def set_texture(self, texture: Texture) -> None:
        """
        Set the texture to be rendered on the quad

        Parameter ``texture``:
            The texture to display
        """

    def set_mvp(self, mvp: Matrix4f) -> None:
        """
        Set the model-view-projection matrix

        Parameter ``mvp``:
            The transformation matrix
        """

    def set_texture_linear(self, linear: bool) -> None:
        """
        Set whether the texture is in linear space

        When true, the shader will convert from linear to sRGB space.
        When false, the texture is assumed to already be in sRGB space.
        Default is ``false``.

        Parameter ``linear``:
            True if texture is in linear space, false if in sRGB space
        """

    def texture_linear(self) -> bool:
        """
        Get whether the texture is treated as linear space

        Returns:
            True if texture is treated as linear space
        """

    def set_texture_exposure(self, exposure: float) -> None:
        """
        Set the exposure multiplier for the texture

        This value is multiplied onto the texture color before
        linear-to-sRGB conversion. Default is 1.0.

        Parameter ``exposure``:
            Exposure multiplier (typically 0.0 to 10.0)
        """

    def texture_exposure(self) -> float:
        """
        Get the current exposure multiplier

        Returns:
            Current exposure value
        """

    def draw(self) -> None:
        """
        Render the quad

        This method handles begin(), draw_array(), and end() internally
        """

def cmake_dir(): ...
