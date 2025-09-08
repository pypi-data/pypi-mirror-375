/*
    NanoGUI was developed by Wenzel Jakob <wenzel.jakob@epfl.ch>.
    The widget drawing code is based on the NanoVG demo application
    by Mikko Mononen.

    All rights reserved. Use of this source code is governed by a
    BSD-style license that can be found in the LICENSE.txt file.
*/

/**
 * \file nanogui/common.h
 *
 * \brief Common definitions used by NanoGUI.
 */

#pragma once

#include <cstdint>
#include <utility>
#include <functional>
#include <string>
#include <string_view>
#include <vector>
#include <stdexcept>
#include <cassert>

#define NANOGUI_VERSION_MAJOR 0
#define NANOGUI_VERSION_MINOR 3
#define NANOGUI_VERSION_PATCH 0

#define NANOGUI_STRINGIFY(x) #x
#define NANOGUI_TOSTRING(x)  NANOGUI_STRINGIFY(x)
#define NANOGUI_VERSION                                                          \
    (NANOGUI_TOSTRING(NANOGUI_VERSION_MAJOR) "."                                 \
     NANOGUI_TOSTRING(NANOGUI_VERSION_MINOR) "."                                 \
     NANOGUI_TOSTRING(NANOGUI_VERSION_PATCH))

/* Set to 1 to draw boxes around widgets */
//#define NANOGUI_SHOW_WIDGET_BOUNDS 1

#if !defined(NAMESPACE_BEGIN) || defined(DOXYGEN_DOCUMENTATION_BUILD)
    /**
     * \brief Convenience macro for namespace declarations
     *
     * The macro ``NAMESPACE_BEGIN(nanogui)`` will expand to ``namespace
     * nanogui {``. This is done to hide the namespace scope from editors and
     * C++ code formatting tools that may otherwise indent the entire file.
     * The corresponding ``NAMESPACE_END`` macro also lists the namespace
     * name for improved readability.
     *
     * \param name
     *     The name of the namespace scope to open
     */
    #define NAMESPACE_BEGIN(name) namespace name {
#endif
#if !defined(NAMESPACE_END) || defined(DOXYGEN_DOCUMENTATION_BUILD)
    /**
     * \brief Convenience macro for namespace declarations
     *
     * Closes a namespace (counterpart to ``NAMESPACE_BEGIN``)
     * ``NAMESPACE_END(nanogui)`` will expand to only ``}``.
     *
     * \param name
     *     The name of the namespace scope to close
     */
    #define NAMESPACE_END(name) }
#endif

#if defined(NANOGUI_SHARED)
#  if defined(_WIN32)
#    if defined(NANOGUI_BUILD)
#      define NANOGUI_EXPORT __declspec(dllexport)
#    else
#      define NANOGUI_EXPORT __declspec(dllimport)
#    endif
#  elif defined(NANOGUI_BUILD)
#    define NANOGUI_EXPORT __attribute__ ((visibility("default")))
#  else
#    define NANOGUI_EXPORT
#  endif
#else
     /**
      * If the build flag ``NANOGUI_SHARED`` is defined, this directive will expand
      * to be the platform specific shared library import / export command depending
      * on the compilation stage.  If undefined, it expands to nothing. **Do not**
      * define this directive on your own.
      */
#    define NANOGUI_EXPORT
#endif

/* Force usage of discrete GPU on laptops (macro must be invoked in main application) */
#if defined(_WIN32) && !defined(DOXYGEN_DOCUMENTATION_BUILD)
#define NANOGUI_FORCE_DISCRETE_GPU() \
    extern "C" { \
        __declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 1; \
        __declspec(dllexport) int NvOptimusEnablement = 1; \
    }
#else
/**
 * On Windows, exports ``AmdPowerXpressRequestHighPerformance`` and
 * ``NvOptimusEnablement`` as ``1``.
 */
#define NANOGUI_FORCE_DISCRETE_GPU()
#endif

#if defined(_MSC_VER)
#  if defined(NANOGUI_BUILD)
/* Quench a few warnings on when compiling NanoGUI on Windows with MSVC */
#    pragma warning(disable : 4127) // warning C4127: conditional expression is constant
#    pragma warning(disable : 4244) // warning C4244: conversion from X to Y, possible loss of data
#  endif
#  pragma warning(disable : 4251) // warning C4251: class X needs to have dll-interface to be used by clients of class Y
#  pragma warning(disable : 4714) // warning C4714: function X marked as __forceinline not inlined
#endif

// These will produce broken links in the docs build
#if !defined(DOXYGEN_SHOULD_SKIP_THIS)

extern "C" {
    /* Opaque handle types */
    typedef struct NVGcontext NVGcontext;
    typedef struct GLFWwindow GLFWwindow;
}

struct NVGcolor;
struct NVGglyphPosition;
struct GLFWcursor;

#endif // DOXYGEN_SHOULD_SKIP_THIS

// Define command key for windows/mac/linux
#if defined(__APPLE__) || defined(DOXYGEN_DOCUMENTATION_BUILD)
    /// If on OSX, maps to ``GLFW_MOD_SUPER``.  Otherwise, maps to ``GLFW_MOD_CONTROL``.
    #define SYSTEM_COMMAND_MOD GLFW_MOD_SUPER
#else
    #define SYSTEM_COMMAND_MOD GLFW_MOD_CONTROL
#endif

NAMESPACE_BEGIN(nanogui)

/// Cursor shapes available to use in GLFW.  Shape of actual cursor determined by Operating System.
enum class Cursor {
    Arrow = 0,  ///< The arrow cursor.
    IBeam,      ///< The I-beam cursor.
    Crosshair,  ///< The crosshair cursor.
    Hand,       ///< The hand cursor.
    HResize,    ///< The horizontal resize cursor.
    VResize,    ///< The vertical resize cursor.
    CursorCount ///< Not a cursor --- should always be last: enables a loop over the cursor types.
};

// skip the forward declarations for the docs
#ifndef DOXYGEN_SHOULD_SKIP_THIS

/* Forward declarations */
template <typename T> class ref;
class AdvancedGridLayout;
class BoxLayout;
class Button;
class CheckBox;
class Canvas;
class ColorWheel;
class ColorPicker;
class ComboBox;
class GLFramebuffer;
class GLShader;
class GridLayout;
class GroupLayout;
class ImagePanel;
class ImageView;
class Label;
class Layout;
class MessageDialog;
class Object;
class Popup;
class PopupButton;
class ProgressBar;
class RenderPass;
class Shader;
class Screen;
class Serializer;
class Slider;
class TabWidgetBase;
class TabWidget;
class TextBox;
class TextArea;
class Texture;
class Theme;
class ToolButton;
class VScrollPanel;
class Widget;
class Window;

#endif // DOXYGEN_SHOULD_SKIP_THIS

/**
 * Static initialization; should be called once before invoking **any** NanoGUI
 * functions **if** you are having NanoGUI manage OpenGL / GLFW.  This method
 * is effectively a wrapper call to ``glfwInit()``, so if you are managing
 * OpenGL / GLFW on your own *do not call this method*.
 *
 * \rst
 * Refer to :ref:`nanogui_example_3` for how you might go about managing OpenGL
 * and GLFW on your own, while still using NanoGUI's classes.
 * \endrst
 */
extern NANOGUI_EXPORT void init(bool color_management = false);

/// Static shutdown; should be called before the application terminates.
extern NANOGUI_EXPORT void shutdown();

/// The nanogui mainloop can be in the following set of states
enum class RunMode : uint32_t {
    /// The mainloop is currently stopped
    Stopped,

    /// Windows are redrawn lazily as events arrive
    Lazy,

    /// Windows are redrawn based on the screen's refresh rate
    VSync,

    /// Windows are redrawn as quickly as possible. Will use 100% CPU.
    Eager
};

/**
 * \brief Enter the application main loop
 *
 * \param mode
 *     By default, NanoGUI redraws the window contents based on the screen's
 *     native refresh rate (e.g., 60FPS). To save power, prefer \ref
 *     RunMode::Lazy, which only redraws when processing of keyboard/mouse/..
 *     events explicitly *requests* a redraw by returning \c true. A manual
 *     redraw can also be triggered using \ref Screen::redraw(). The last
 *     option, \ref RunMode::Eager, runs the main loop while merely polling for
 *     events, which will use 100% CPU.
 */
extern NANOGUI_EXPORT void run(RunMode mode = RunMode::VSync);

/// Adjust the application's run mode following a call to \ref run().
extern NANOGUI_EXPORT void set_run_mode(RunMode mode);

/// Query the application's run mode
extern NANOGUI_EXPORT RunMode run_mode();

/// Terminate the main loop
inline void leave() { set_run_mode(RunMode::Stopped); }

/// Check if the main loop is still active
inline bool active() { return run_mode() != RunMode::Stopped; }

/**
 * \brief Enqueue a function to be executed executed before
 * the application is redrawn the next time.
 *
 * NanoGUI is not thread-safe, and async() provides a mechanism
 * for queuing up UI-related state changes from other threads.
 */
extern NANOGUI_EXPORT void async(const std::function<void()> &func);

/**
 * \brief Check for the availability of displays with 10-bit color and/or
 * extended dynamic range (EDR), i.e. the ability to reproduce intensities
 * exceeding the standard dynamic range from 0.0-1.0.
 *
 * To leverage either of these features, you will need to create a \ref Screen
 * with <tt>float_buffer=True</tt>. Only the macOS Metal backend of NanoGUI
 * implements this function right now. All other platforms return <tt>(false,
 * false)</tt>.
 *
 * \return A <tt>std::pair</tt> with two boolean values. The first indicates
 * 10-bit color support, and the second indicates EDR support.
 */
extern NANOGUI_EXPORT std::pair<bool, bool> test_10bit_edr_support();

/// Selection of file/folder dialog types supported by file_dialog()
enum class FileDialogType {
    /// Open a single file
    Open,

    /// Open multiple files
    OpenMultiple,

    /// Save a single file
    Save,

    /// Pick a single folder (``filters`` not supported)
    PickFolder,

    /// Pick multiple folders (``filters`` argument must be empty)
    PickFolderMultiple
};

/**
 * \brief Open a native file/folder dialog
 *
 * This function can instantiate variety of file dialogs using native UI
 * widgets. This functionality is bsaed on the bundled
 * ``nativefiledialog-extended`` [1] library.
 *
 * [1] https://github.com/btzy/nativefiledialog-extended
 *
 * \param type
 *     The type of dialog. For \ref FileDialogType::Open, \ref FileDialogType::Save,
 *     and \ref FileDialogType::PickFolder, the output array contains at most one
 *     entry.
 *
 * \param filter
 *     Specify file formats with descriptions to indicate a preference for specific
 *     file types.
 *
 * \param default_path
 *     If specified, the OS dialog will show files/folders at a specified starting
 *     location.
 */
extern NANOGUI_EXPORT std::vector<std::string>
file_dialog(Widget *parent,
            FileDialogType type,
            const std::vector<std::pair<std::string, std::string>> &filters = {},
            const std::string &default_path = {});

#if defined(__APPLE__) || defined(DOXYGEN_DOCUMENTATION_BUILD)
/**
 * \brief Move to the application bundle's parent directory
 *
 * This is function is convenient when deploying .app bundles on OSX. It
 * adjusts the file path to the parent directory containing the bundle.
 */
extern NANOGUI_EXPORT void chdir_to_bundle_parent();
#endif

/**
 * \brief Convert a single UTF32 character code to UTF8.
 *
 * \rst
 * NanoGUI uses this to convert the icon character codes
 * defined in :ref:`file_nanogui_entypo.h`.
 * \endrst
 *
 * \param c
 *     The UTF32 character to be converted.
 */
extern NANOGUI_EXPORT std::string utf8(uint32_t c);

/// Load a directory of PNG images and upload them to the GPU (suitable for use with ImagePanel)
extern NANOGUI_EXPORT std::vector<std::pair<int, std::string>>
    load_image_directory(NVGcontext *ctx, const std::string &path);

/// Convenience function for instanting a PNG icon from the application's data segment (via bin2c)
#define nvgImageIcon(ctx, name) nanogui::__nanogui_get_image(ctx, #name, name##_png, name##_png_size)
/// Helper function used by nvg_image_icon
extern NANOGUI_EXPORT int __nanogui_get_image(NVGcontext *ctx, std::string_view name,
                                              uint8_t *data, uint32_t size);

NAMESPACE_END(nanogui)

NAMESPACE_BEGIN(drjit)
/// Base class of all Dr.Jit arrays
template <typename Value_, bool IsMask_, typename Derived_> struct ArrayBase;
NAMESPACE_END(drjit)

