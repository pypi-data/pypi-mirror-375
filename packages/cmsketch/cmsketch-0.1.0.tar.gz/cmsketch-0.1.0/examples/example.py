#!/usr/bin/env python3
"""
Example usage of the Count-Min Sketch library
"""

import cmsketch


def main():
    print("Count-Min Sketch Example")
    print(f"Version: {cmsketch.__version__}")

    # Create a sketch with width=1000, depth=5
    sketch = cmsketch.PyCountMinSketch(1000, 5)

    # Add some elements
    elements = [
        "apple",
        "banana",
        "apple",
        "cherry",
        "banana",
        "apple",
        "date",
        "elderberry",
        "fig",
        "grape",
        "apple",
        "banana",
    ]

    print("\nAdding elements to sketch:")
    for element in elements:
        sketch.insert(element)
        print(f"Added: {element}")

    # Query frequencies
    print("\nEstimated frequencies:")
    queries = ["apple", "banana", "cherry", "unknown"]

    for query in queries:
        estimate = sketch.count(query)
        print(f"{query}: {estimate}")

    # Test TopK functionality
    print("\nTop 3 elements:")
    top_k = sketch.top_k(3, queries)
    for item, count in top_k:
        print(f"{item}: {count}")

    print(f"Sketch dimensions: {sketch.get_width()} x {sketch.get_depth()}")

    # Test with integer keys
    print("\n--- Testing with integer keys ---")
    int_sketch = cmsketch.PyCountMinSketchInt(100, 3)

    int_elements = [1, 2, 1, 3, 2, 1, 4, 5]
    for element in int_elements:
        int_sketch.insert(element)

    print("Integer sketch counts:")
    for i in range(1, 6):
        count = int_sketch.count(i)
        print(f"{i}: {count}")


if __name__ == "__main__":
    main()
