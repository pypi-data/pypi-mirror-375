#include "cmsketch/count_min_sketch.h"
#include <algorithm>
#include <cstddef>
#include <format>
#include <stdexcept>
#include <string>

namespace cmsketch {

/**
 * Constructor for the count-min sketch.
 *
 * @param width The width of the sketch matrix.
 * @param depth The depth of the sketch matrix.
 * @throws std::invalid_argument if width or depth are zero.
 */
template <typename KeyType>
CountMinSketch<KeyType>::CountMinSketch(uint32_t width, uint32_t depth)
    : width_(width), depth_(depth) {

  // Throw an error if width or depth are zero
  if (width == 0 || depth == 0) {
    throw std::invalid_argument(std::format(
        "Width and depth must be greater than zero; Got width: {}, depth: {}",
        width, depth));
  }

  // Initialize the table with zeros
  sketch_matrix_ =
      std::make_unique<std::vector<std::atomic<uint32_t>>>(width_ * depth_);

  // Initialize seeded hash functions
  hash_functions_.reserve(depth_);
  for (size_t i = 0; i < depth_; i++) {
    hash_functions_.push_back(this->HashFunction(i));
  }
}

template <typename KeyType>
CountMinSketch<KeyType>::CountMinSketch(CountMinSketch &&other) noexcept
    : width_(other.width_), depth_(other.depth_) {

  // Do nothing if the other sketch is the same
  if (this == &other) {
    return;
  }

  // Move the table and hash functions
  sketch_matrix_ = std::move(other.sketch_matrix_);
  hash_functions_ = std::move(other.hash_functions_);
}

template <typename KeyType>
auto CountMinSketch<KeyType>::operator=(CountMinSketch &&other) noexcept
    -> CountMinSketch & {

  // Do nothing if the other sketch is the same
  if (this == &other) {
    return *this;
  }

  // Set the width and depth
  width_ = other.width_;
  depth_ = other.depth_;

  // Move the table and hash functions
  sketch_matrix_ = std::move(other.sketch_matrix_);
  hash_functions_ = std::move(other.hash_functions_);

  return *this;
}

template <typename KeyType>
void CountMinSketch<KeyType>::Insert(const KeyType &item) {

  for (size_t i = 0; i < depth_; i++) {
    // Get the hash function
    auto hash_function = hash_functions_[i];

    // Hash the item and get the column index
    auto column_index = hash_function(item);

    // Increment the count in the table
    sketch_matrix_->at(i * width_ + column_index).fetch_add(1);
  }
}

template <typename KeyType>
void CountMinSketch<KeyType>::Merge(const CountMinSketch<KeyType> &other) {
  if (width_ != other.width_ || depth_ != other.depth_) {
    throw std::invalid_argument(
        "Incompatible CountMinSketch dimensions for merge.");
  }
  /** @TODO(student) Implement this function! */

  for (size_t i = 0; i < width_ * depth_; i++) {
    // Get the count in the cell of the other sketch
    auto count = other.sketch_matrix_->at(i).load();

    // Increment the count in the current sketch
    sketch_matrix_->at(i).fetch_add(count);
  }
}

template <typename KeyType>
auto CountMinSketch<KeyType>::Count(const KeyType &item) const -> uint32_t {
  // Initialize the minimum count to the maximum possible value
  uint32_t min_count = std::numeric_limits<uint32_t>::max();

  for (size_t i = 0; i < depth_; i++) {
    // Get the hash function
    auto hash_function = hash_functions_[i];

    // Hash the item and get the column index
    auto column_index = hash_function(item);

    // Get the count in this row
    auto count = sketch_matrix_->at(i * width_ + column_index)
                     .load(std::memory_order_relaxed);

    // Update the minimum count
    if (count < min_count) {
      min_count = count;
    }
  }

  return min_count;
}

template <typename KeyType> void CountMinSketch<KeyType>::Clear() {
  /** @TODO(student) Implement this function! */

  // Zero out the sketch matrix
  std::fill(sketch_matrix_->begin(), sketch_matrix_->end(), 0);
}

template <typename KeyType>
auto CountMinSketch<KeyType>::TopK(uint16_t k,
                                   const std::vector<KeyType> &candidates)
    -> std::vector<std::pair<KeyType, uint32_t>> {
  /** @TODO(student) Implement this function! */

  // Calculate counts of all candidates
  size_t n = candidates.size();
  std::vector<std::pair<KeyType, uint32_t>> counts(n);
  for (size_t i = 0; i < n; i++) {
    counts[i] = std::make_pair(candidates[i], this->Count(candidates[i]));
  }

  // Sort the counts with respect to the second element
  std::sort(counts.begin(), counts.end(),
            [](const std::pair<KeyType, uint32_t> &a,
               const std::pair<KeyType, uint32_t> &b) {
              return a.second > b.second;
            });

  // Slice the counts to the first k elements
  counts = std::vector<std::pair<KeyType, uint32_t>>(counts.begin(),
                                                     counts.begin() + k);

  return counts;
}

// Explicit instantiations for all types used in tests
template class CountMinSketch<std::string>;
template class CountMinSketch<int64_t>; // For int64_t tests
template class CountMinSketch<int>;     // This covers both int and int32_t
} // namespace cmsketch
