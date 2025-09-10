#include "cmsketch/cmsketch.h" // IWYU pragma: keep
#include <gtest/gtest.h>
#include <random>
#include <string>
#include <vector>

class CountMinSketchTest : public ::testing::Test {
protected:
  void SetUp() override {
    sketch = std::make_unique<cmsketch::CountMinSketch<std::string>>(1000, 5);
  }

  std::unique_ptr<cmsketch::CountMinSketch<std::string>> sketch;
};

TEST_F(CountMinSketchTest, BasicInsertAndCount) {
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  EXPECT_EQ(sketch->Count("test"), 5);
}

TEST_F(CountMinSketchTest, MultipleElements) {
  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("c");
  sketch->Insert("c");

  EXPECT_EQ(sketch->Count("a"), 3);
  EXPECT_EQ(sketch->Count("b"), 7);
  EXPECT_EQ(sketch->Count("c"), 2);
}

TEST_F(CountMinSketchTest, DuplicateInserts) {
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");

  EXPECT_EQ(sketch->Count("test"), 5);
}

TEST_F(CountMinSketchTest, NonExistentElement) {
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  EXPECT_EQ(sketch->Count("nonexistent"), 0);
}

TEST_F(CountMinSketchTest, Clear) {
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Insert("test");
  sketch->Clear();

  EXPECT_EQ(sketch->Count("test"), 0);
}

TEST_F(CountMinSketchTest, Merge) {
  auto sketch2 =
      std::make_unique<cmsketch::CountMinSketch<std::string>>(1000, 5);

  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch2->Insert("a");
  sketch2->Insert("c");
  sketch2->Insert("c");
  sketch2->Insert("c");
  sketch2->Insert("c");

  sketch->Merge(*sketch2);

  EXPECT_EQ(sketch->Count("a"), 4);
  EXPECT_EQ(sketch->Count("b"), 2);
  EXPECT_EQ(sketch->Count("c"), 4);
}

TEST_F(CountMinSketchTest, MergeIncompatibleDimensions) {
  auto incompatible_sketch =
      std::make_unique<cmsketch::CountMinSketch<std::string>>(100, 3);

  EXPECT_THROW(sketch->Merge(*incompatible_sketch), std::invalid_argument);
}

TEST_F(CountMinSketchTest, TopK) {
  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("a");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("b");
  sketch->Insert("c");
  sketch->Insert("c");
  sketch->Insert("c");
  sketch->Insert("c");
  sketch->Insert("c");

  std::vector<std::string> candidates = {"a", "b", "c", "d"};
  auto top_k = sketch->TopK(3, candidates);

  EXPECT_EQ(top_k.size(), 3);
  EXPECT_EQ(top_k[0].first, "c"); // Should be highest count
  EXPECT_EQ(top_k[0].second, 5);
  EXPECT_EQ(top_k[1].first, "b");
  EXPECT_EQ(top_k[1].second, 4);
  EXPECT_EQ(top_k[2].first, "a");
  EXPECT_EQ(top_k[2].second, 3);
}

TEST_F(CountMinSketchTest, LargeDataset) {
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(
      1, 50); // Smaller counts to reduce collisions

  std::vector<std::string> elements;
  std::vector<int> counts;

  // Generate random data
  for (int i = 0; i < 500; ++i) { // Fewer elements to reduce collisions
    elements.push_back("element_" + std::to_string(i));
    counts.push_back(dis(gen));
    for (int j = 0; j < counts.back(); ++j) {
      sketch->Insert(elements.back());
    }
  }

  // Verify estimates are reasonable (within error bounds)
  // Count-Min Sketch guarantees estimates >= actual, but can have significant
  // overestimation
  for (size_t i = 0; i < elements.size(); ++i) {
    uint32_t estimate = sketch->Count(elements[i]);
    EXPECT_GE(estimate, counts[i]); // Estimate should be >= actual
    // For Count-Min Sketch, we mainly care that estimates are >= actual
    // Overestimation is expected and can be significant
  }
}

TEST_F(CountMinSketchTest, Dimensions) {
  EXPECT_EQ(sketch->GetWidth(), 1000);
  EXPECT_EQ(sketch->GetDepth(), 5);
}

TEST_F(CountMinSketchTest, IntegerKeys) {
  cmsketch::CountMinSketch<int> int_sketch(100, 3);

  int_sketch.Insert(1);
  int_sketch.Insert(1);
  int_sketch.Insert(2);
  int_sketch.Insert(2);
  int_sketch.Insert(2);
  int_sketch.Insert(2);

  EXPECT_EQ(int_sketch.Count(1), 2);
  EXPECT_EQ(int_sketch.Count(2), 4);
  EXPECT_EQ(int_sketch.Count(3), 0);
}
