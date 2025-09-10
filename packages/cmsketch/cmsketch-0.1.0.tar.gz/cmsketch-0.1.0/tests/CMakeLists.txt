# Test configuration
find_package(GTest REQUIRED)

# Auto-detect test source files
file(GLOB TEST_SOURCES "*.cc" "*.cpp")

# Create test executable
add_executable(cmsketch_tests ${TEST_SOURCES})

# Link libraries
target_link_libraries(cmsketch_tests PRIVATE cmsketch GTest::gtest
                                             GTest::gtest_main)

# Include directories
target_include_directories(cmsketch_tests PRIVATE ${CMAKE_SOURCE_DIR}/include)

# Add tests to CTest
add_test(NAME cmsketch_tests COMMAND cmsketch_tests)
