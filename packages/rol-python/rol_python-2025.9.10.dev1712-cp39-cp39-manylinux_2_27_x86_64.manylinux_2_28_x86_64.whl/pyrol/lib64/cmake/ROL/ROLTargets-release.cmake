#----------------------------------------------------------------
# Generated CMake target import file for configuration "RELEASE".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ROL::rol" for configuration "RELEASE"
set_property(TARGET ROL::rol APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ROL::rol PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/librol.so.16.2.0"
  IMPORTED_SONAME_RELEASE "librol.so.16"
  )

list(APPEND _cmake_import_check_targets ROL::rol )
list(APPEND _cmake_import_check_files_for_ROL::rol "${_IMPORT_PREFIX}/lib64/librol.so.16.2.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
