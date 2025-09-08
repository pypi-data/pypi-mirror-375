#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "nanogui" for configuration "Release"
set_property(TARGET nanogui APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nanogui PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/nanogui/nanogui.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/nanogui/nanogui.dll"
  )

list(APPEND _cmake_import_check_targets nanogui )
list(APPEND _cmake_import_check_files_for_nanogui "${_IMPORT_PREFIX}/nanogui/nanogui.lib" "${_IMPORT_PREFIX}/nanogui/nanogui.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
