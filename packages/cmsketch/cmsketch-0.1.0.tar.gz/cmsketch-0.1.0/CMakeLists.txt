cmake_minimum_required(VERSION 3.15)

# Project configuration
project(
  cmsketch
  VERSION 1.0.0
  DESCRIPTION "High-performance Count-Min Sketch implementation in C++"
  LANGUAGES CXX)

# Generate compile_commands.json for better IDE support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Set C++ standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set default build type to Release if not specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE
      Release
      CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
                                               "MinSizeRel" "RelWithDebInfo")
endif()

# Add compile definitions for better debugging
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  add_compile_definitions(DEBUG=1)
else()
  add_compile_definitions(NDEBUG=1)
endif()

# Compiler-specific options
if(MSVC)
  add_compile_options(/W4 /WX)
else()
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Auto-detect source files
file(GLOB_RECURSE CMSKETCH_SOURCES "src/cmsketch/*.cc" "src/cmsketch/*.cpp")

# Auto-detect header files
file(GLOB_RECURSE CMSKETCH_HEADERS "include/cmsketch/*.h"
     "include/cmsketch/*.hpp")

# Create the main library
add_library(cmsketch ${CMSKETCH_SOURCES})

# Set target properties for better IDE support
target_include_directories(
  cmsketch PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                  $<INSTALL_INTERFACE:include>)
target_compile_features(cmsketch PUBLIC cxx_std_23)

# Auto-detect example source files
file(GLOB EXAMPLE_SOURCES "src/main.cc" "src/main.cpp")

# Create example executable
add_executable(cmsketch_example ${EXAMPLE_SOURCES})
target_link_libraries(cmsketch_example PRIVATE cmsketch)

# Set target properties
set_target_properties(
  cmsketch
  PROPERTIES VERSION ${PROJECT_VERSION}
             SOVERSION ${PROJECT_VERSION_MAJOR}
             PUBLIC_HEADER include/cmsketch/cmsketch.h)

# Install targets
install(
  TARGETS cmsketch
  EXPORT cmsketchTargets
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
  PUBLIC_HEADER DESTINATION include/cmsketch)

# Install headers
install(
  DIRECTORY include/cmsketch/
  DESTINATION include/cmsketch
  FILES_MATCHING
  PATTERN "*.h")

# Export targets (simplified - no complex package config needed)
install(
  EXPORT cmsketchTargets
  FILE cmsketchTargets.cmake
  NAMESPACE cmsketch::
  DESTINATION lib/cmake/cmsketch)

# Find pybind11 for IDE support (always try to find it)
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG)

# Python bindings (only if building with scikit-build)
if(SKBUILD_PROJECT_NAME AND pybind11_FOUND)
  # Auto-detect Python bindings source
  file(GLOB PYTHON_BINDINGS_SOURCES "src/python_bindings.cc"
       "src/python_bindings.cpp")
  pybind11_add_module(_core MODULE ${PYTHON_BINDINGS_SOURCES})
  target_link_libraries(_core PRIVATE cmsketch)
  install(TARGETS _core DESTINATION ${SKBUILD_PROJECT_NAME})
endif()

# Optional Python bindings target for development/IDE support
option(BUILD_PYTHON_BINDINGS "Build Python bindings for development" OFF)
if(BUILD_PYTHON_BINDINGS AND pybind11_FOUND)
  # Auto-detect Python bindings source
  file(GLOB PYTHON_BINDINGS_SOURCES "src/python_bindings.cc"
       "src/python_bindings.cpp")
  pybind11_add_module(_core_dev MODULE ${PYTHON_BINDINGS_SOURCES})
  target_link_libraries(_core_dev PRIVATE cmsketch)
  set_target_properties(_core_dev PROPERTIES OUTPUT_NAME "_core")
endif()

# Testing (only if enabled)
option(BUILD_TESTS "Build tests" OFF)
if(BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()

# Documentation (only if enabled)
option(BUILD_DOCS "Build documentation" OFF)
if(BUILD_DOCS)
  find_package(Doxygen REQUIRED)
  add_subdirectory(docs)
endif()

# Add custom targets for common tasks
add_custom_target(
  format
  COMMAND
    find ${CMAKE_SOURCE_DIR}/src ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/tests -name "*.cc" -o -name "*.h" | xargs clang-format
    -i
  COMMENT "Formatting source code with clang-format"
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

add_custom_target(
  clean-all
  COMMAND ${CMAKE_COMMAND} -E remove_directory ${CMAKE_BINARY_DIR}
  COMMENT "Removing all build files")

# Print configuration summary
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Source files: ${CMSKETCH_SOURCES}")
message(STATUS "Header files: ${CMSKETCH_HEADERS}")
