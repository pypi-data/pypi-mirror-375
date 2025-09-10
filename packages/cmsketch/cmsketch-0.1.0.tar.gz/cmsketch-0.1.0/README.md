# Count-Min Sketch

A high-performance, template-based C++ implementation of the Count-Min Sketch probabilistic data structure with Python bindings.

## Features

- **Template-Based Design**: Supports any hashable key type (strings, integers, etc.)
- **Thread-Safe**: Uses atomic operations for concurrent access
- **High Performance**: Optimized C++ implementation with efficient memory usage
- **Python Bindings**: Easy-to-use Python interface via pybind11
- **Comprehensive Testing**: Full test suite with Google Test
- **CMake Build System**: Modern, cross-platform build configuration

## Project Structure

```
count-min-sketch/
├── include/cmsketch/           # Public header files
│   ├── cmsketch.h             # Main header (include this)
│   ├── count_min_sketch.h     # Core Count-Min Sketch template class
│   ├── hash_util.h            # Hash utility functions
│   └── version.h              # Version information
├── src/cmsketch/              # C++ source files
│   ├── count_min_sketch.cc    # Core implementation
│   └── version.cc             # Version implementation
├── src/                       # Additional source files
│   ├── main.cc               # Example application
│   └── python_bindings.cc    # Python bindings
├── tests/                     # Unit tests
│   ├── CMakeLists.txt        # Test configuration
│   ├── test_count_min_sketch.cpp
│   ├── test_hash_functions.cpp
│   └── test_sketch_config.cpp
├── docs/                      # Documentation
│   ├── CMakeLists.txt        # Documentation build
│   └── Doxyfile.in           # Doxygen configuration
├── cmake/                     # CMake modules
│   └── cmsketchConfig.cmake.in
├── CMakeLists.txt            # Main build configuration
├── pyproject.toml            # Python package configuration
├── example.py                # Python example
└── build.sh                  # Build script
```

## Building

### Prerequisites

- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.15+
- Python 3.11+ (for Python bindings)
- pybind11 (for Python bindings)
- Google Test (for testing, optional)

### Quick Build

```bash
# Make build script executable
chmod +x build.sh

# Build everything
./build.sh
```

### Manual Build

```bash
# Create build directory
mkdir build && cd build

# Configure
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
make -j$(nproc)

# Run tests (optional)
make test

# Run example
./cmsketch_example
```

### Python Package

```bash
# Install Python dependencies
pip install pybind11 scikit-build-core

# Build Python package
pip install .
```

## Usage

### C++ Example

```cpp
#include "cmsketch/cmsketch.h"
#include <iostream>
#include <vector>

int main() {
    // Create a sketch with width=1000, depth=5
    cmsketch::CountMinSketch<std::string> sketch(1000, 5);
    
    // Add elements
    sketch.Insert("apple");
    sketch.Insert("apple");
    sketch.Insert("apple");
    sketch.Insert("banana");
    sketch.Insert("banana");
    sketch.Insert("apple");
    
    // Query frequencies
    std::cout << "apple: " << sketch.Count("apple") << std::endl;    // 4
    std::cout << "banana: " << sketch.Count("banana") << std::endl;  // 2
    std::cout << "cherry: " << sketch.Count("cherry") << std::endl;  // 0
    
    // Test TopK functionality
    std::vector<std::string> candidates = {"apple", "banana", "cherry"};
    auto top_k = sketch.TopK(2, candidates);
    for (const auto& pair : top_k) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }
    
    return 0;
}
```

### Python Example

```python
import cmsketch

# Create a sketch
sketch = cmsketch.CountMinSketch(1000, 5)

# Add elements
sketch.insert("apple")
sketch.insert("apple")
sketch.insert("apple")
sketch.insert("banana")
sketch.insert("banana")
sketch.insert("apple")

# Query frequencies
print(f"apple: {sketch.count('apple')}")    # 4
print(f"banana: {sketch.count('banana')}")  # 2
print(f"cherry: {sketch.count('cherry')}")  # 0

# Test TopK functionality
candidates = ["apple", "banana", "cherry"]
top_k = sketch.top_k(2, candidates)
for item, count in top_k:
    print(f"{item}: {count}")
```

## API Reference

### Core Classes

- **`CountMinSketch<KeyType>`**: Template-based sketch implementation
- **`HashUtil`**: Hash utility functions
- **`Version`**: Version information

### Key Methods

- `Insert(item)`: Insert an item into the sketch
- `Count(item)`: Get estimated count of an item
- `Merge(other)`: Merge another sketch
- `Clear()`: Reset sketch to initial state
- `TopK(k, candidates)`: Get top k items from candidates
- `GetWidth()`: Get sketch width
- `GetDepth()`: Get sketch depth

## Configuration

The sketch is configured with explicit dimensions:

```cpp
// String keys
cmsketch::CountMinSketch<std::string> sketch(1000, 5);

// Integer keys
cmsketch::CountMinSketch<int> int_sketch(100, 3);

// Int64 keys
cmsketch::CountMinSketch<int64_t> int64_sketch(500, 4);
```

## Error Bounds

The Count-Min Sketch provides the following guarantees:

- **Overestimate**: Estimates are always ≥ actual frequency
- **Error Bound**: Error is bounded by the sketch dimensions
- **Memory**: O(width × depth) counters
- **Thread Safety**: Atomic operations ensure thread-safe concurrent access

## Testing

Run the test suite:

```bash
cd build
make test
# or
./cmsketch_tests
```

## Documentation

Generate API documentation:

```bash
cd build
make docs
# Documentation will be in docs/html/
```

## Contributing

1. Follow Google C++ Style Guide
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass

## License

[Add your license here]
