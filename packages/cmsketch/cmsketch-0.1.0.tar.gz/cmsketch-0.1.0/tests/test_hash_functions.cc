#include "cmsketch/cmsketch.h" // IWYU pragma: keep
#include <gtest/gtest.h>
#include <string>
#include <unordered_set>

class HashFunctionsTest : public ::testing::Test {
protected:
  void SetUp() override {
    test_strings = {"hello", "world", "test", "hash", "function",
                    "a",     "ab",    "abc",  "abcd", "abcde",
                    "",      " ",     "  ",   "\n",   "\t"};
  }

  std::vector<std::string> test_strings;
};

TEST_F(HashFunctionsTest, HashUtilConsistency) {
  // Test HashUtil::HashBytes consistency
  for (const auto &str : test_strings) {
    auto hash1 = cmsketch::HashUtil::HashBytes(str.c_str(), str.length());
    auto hash2 = cmsketch::HashUtil::HashBytes(str.c_str(), str.length());
    EXPECT_EQ(hash1, hash2);
  }
}

TEST_F(HashFunctionsTest, HashUtilDifferentInputs) {
  // Test that different inputs produce different hashes
  auto hash1 = cmsketch::HashUtil::HashBytes("hello", 5);
  auto hash2 = cmsketch::HashUtil::HashBytes("world", 5);
  EXPECT_NE(hash1, hash2);
}

TEST_F(HashFunctionsTest, CombineHashes) {
  // Test CombineHashes function
  auto hash1 = cmsketch::HashUtil::HashBytes("hello", 5);
  auto hash2 = cmsketch::HashUtil::HashBytes("world", 5);
  auto combined1 = cmsketch::HashUtil::CombineHashes(hash1, hash2);
  auto combined2 = cmsketch::HashUtil::CombineHashes(hash1, hash2);

  EXPECT_EQ(combined1, combined2);
  EXPECT_NE(combined1, hash1);
  EXPECT_NE(combined1, hash2);
}

TEST_F(HashFunctionsTest, CountMinSketchHashDistribution) {
  // Test hash distribution through CountMinSketch
  cmsketch::CountMinSketch<std::string> sketch(1000, 5);

  std::vector<size_t> hash_values;
  for (const auto &str : test_strings) {
    if (!str.empty()) {
      // We can't directly access the hash functions, but we can test
      // that the sketch produces consistent results
      sketch.Insert(str);
      auto count1 = sketch.Count(str);
      auto count2 = sketch.Count(str);
      EXPECT_EQ(count1, count2);
    }
  }
}

TEST_F(HashFunctionsTest, EmptyStringHandling) {
  // Test empty string handling
  auto empty_hash = cmsketch::HashUtil::HashBytes("", 0);
  // Empty string hash can be 0, which is valid
  EXPECT_GE(empty_hash, 0); // Should be non-negative

  // Should be consistent
  auto empty_hash2 = cmsketch::HashUtil::HashBytes("", 0);
  EXPECT_EQ(empty_hash, empty_hash2);
}

TEST_F(HashFunctionsTest, LongStringHandling) {
  // Test with very long string
  std::string long_string(10000, 'a');
  auto hash_value =
      cmsketch::HashUtil::HashBytes(long_string.c_str(), long_string.length());

  // Should produce a valid hash
  EXPECT_NE(hash_value, 0);

  // Should be consistent
  auto hash_value2 =
      cmsketch::HashUtil::HashBytes(long_string.c_str(), long_string.length());
  EXPECT_EQ(hash_value, hash_value2);
}

TEST_F(HashFunctionsTest, HashDistribution) {
  // Test hash distribution quality
  std::unordered_set<size_t> hash_values;

  // Generate hashes for many different inputs
  for (int i = 0; i < 1000; ++i) {
    std::string input = "test_" + std::to_string(i);
    auto hash_value =
        cmsketch::HashUtil::HashBytes(input.c_str(), input.length());
    hash_values.insert(hash_value);
  }

  // Check that we have good distribution (no obvious patterns)
  EXPECT_GT(hash_values.size(), 900); // 90% unique
}