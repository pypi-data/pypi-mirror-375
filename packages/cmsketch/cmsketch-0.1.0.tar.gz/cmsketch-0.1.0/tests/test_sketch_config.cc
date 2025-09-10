#include "cmsketch/cmsketch.h" // IWYU pragma: keep
#include <gtest/gtest.h>

class CountMinSketchConstructorTest : public ::testing::Test {
protected:
  void SetUp() override {}
};

TEST_F(CountMinSketchConstructorTest, ValidDimensions) {
  cmsketch::CountMinSketch<std::string> sketch(1000, 5);
  EXPECT_EQ(sketch.GetWidth(), 1000);
  EXPECT_EQ(sketch.GetDepth(), 5);
}

TEST_F(CountMinSketchConstructorTest, InvalidWidth) {
  EXPECT_THROW(cmsketch::CountMinSketch<std::string>(0, 5),
               std::invalid_argument);
}

TEST_F(CountMinSketchConstructorTest, InvalidDepth) {
  EXPECT_THROW(cmsketch::CountMinSketch<std::string>(100, 0),
               std::invalid_argument);
}

TEST_F(CountMinSketchConstructorTest, BothInvalid) {
  EXPECT_THROW(cmsketch::CountMinSketch<std::string>(0, 0),
               std::invalid_argument);
}

TEST_F(CountMinSketchConstructorTest, LargeDimensions) {
  cmsketch::CountMinSketch<std::string> sketch(10000, 10);
  EXPECT_EQ(sketch.GetWidth(), 10000);
  EXPECT_EQ(sketch.GetDepth(), 10);
}

TEST_F(CountMinSketchConstructorTest, SmallDimensions) {
  cmsketch::CountMinSketch<std::string> sketch(10, 1);
  EXPECT_EQ(sketch.GetWidth(), 10);
  EXPECT_EQ(sketch.GetDepth(), 1);
}

TEST_F(CountMinSketchConstructorTest, IntegerKeys) {
  cmsketch::CountMinSketch<int> sketch(100, 3);
  EXPECT_EQ(sketch.GetWidth(), 100);
  EXPECT_EQ(sketch.GetDepth(), 3);
}

TEST_F(CountMinSketchConstructorTest, Int64Keys) {
  cmsketch::CountMinSketch<int64_t> sketch(500, 4);
  EXPECT_EQ(sketch.GetWidth(), 500);
  EXPECT_EQ(sketch.GetDepth(), 4);
}
