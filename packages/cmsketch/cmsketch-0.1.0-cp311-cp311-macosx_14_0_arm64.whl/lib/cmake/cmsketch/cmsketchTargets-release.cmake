#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cmsketch::cmsketch" for configuration "Release"
set_property(TARGET cmsketch::cmsketch APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(cmsketch::cmsketch PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcmsketch.a"
  )

list(APPEND _cmake_import_check_targets cmsketch::cmsketch )
list(APPEND _cmake_import_check_files_for_cmsketch::cmsketch "${_IMPORT_PREFIX}/lib/libcmsketch.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
