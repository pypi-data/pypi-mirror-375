#include "cmsketch/cmsketch.h" // IWYU pragma: keep
#include <iostream>
#include <string>
#include <vector>

int main() {
  std::cout << "Count-Min Sketch Example" << std::endl;

  // Create a sketch with width=1000, depth=5
  cmsketch::CountMinSketch<std::string> sketch(1000, 5);

  // Add some elements
  std::vector<std::string> elements = {
      "apple", "banana",     "apple", "cherry", "banana", "apple",
      "date",  "elderberry", "fig",   "grape",  "apple",  "banana"};

  std::cout << "\nAdding elements to sketch:" << std::endl;
  for (const auto &element : elements) {
    sketch.Insert(element);
    std::cout << "Added: " << element << std::endl;
  }

  // Query frequencies
  std::cout << "\nEstimated frequencies:" << std::endl;
  std::vector<std::string> queries = {"apple", "banana", "cherry", "unknown"};

  for (const auto &query : queries) {
    uint32_t estimate = sketch.Count(query);
    std::cout << query << ": " << estimate << std::endl;
  }

  // Test TopK functionality
  std::cout << "\nTop 3 elements:" << std::endl;
  auto top_k = sketch.TopK(3, queries);
  for (const auto &pair : top_k) {
    std::cout << pair.first << ": " << pair.second << std::endl;
  }

  std::cout << "Sketch dimensions: " << sketch.GetWidth() << " x "
            << sketch.GetDepth() << std::endl;

  // Test with integer keys
  std::cout << "\n--- Testing with integer keys ---" << std::endl;
  cmsketch::CountMinSketch<int> int_sketch(100, 3);

  std::vector<int> int_elements = {1, 2, 1, 3, 2, 1, 4, 5};
  for (const auto &element : int_elements) {
    int_sketch.Insert(element);
  }

  std::cout << "Integer sketch counts:" << std::endl;
  for (int i = 1; i <= 5; ++i) {
    std::cout << i << ": " << int_sketch.Count(i) << std::endl;
  }

  return 0;
}