#include "cmsketch/cmsketch.h" // IWYU pragma: keep
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Macro to define common CountMinSketch methods for a given type
#define DEFINE_COUNT_MIN_SKETCH_METHODS(class_type, class_name)                \
  py::class_<cmsketch::CountMinSketch<class_type>>(m, class_name)              \
      .def(py::init<uint32_t, uint32_t>(), py::arg("width"), py::arg("depth"), \
           "Create a Count-Min Sketch with specified dimensions")              \
      .def("insert", &cmsketch::CountMinSketch<class_type>::Insert,            \
           py::arg("item"), "Insert an item into the sketch")                  \
      .def("count", &cmsketch::CountMinSketch<class_type>::Count,              \
           py::arg("item"), "Get the estimated count of an item")              \
      .def("clear", &cmsketch::CountMinSketch<class_type>::Clear,              \
           "Reset the sketch to initial state")                                \
      .def("merge", &cmsketch::CountMinSketch<class_type>::Merge,              \
           py::arg("other"), "Merge another sketch into this one")             \
      .def("top_k", &cmsketch::CountMinSketch<class_type>::TopK, py::arg("k"), \
           py::arg("candidates"), "Get the top k items from candidates")       \
      .def("get_width", &cmsketch::CountMinSketch<class_type>::GetWidth,       \
           "Get the width of the sketch")                                      \
      .def("get_depth", &cmsketch::CountMinSketch<class_type>::GetDepth,       \
           "Get the depth of the sketch")

PYBIND11_MODULE(_core, m) {
  m.doc() = "Count-Min Sketch implementation with Python bindings";

  // CountMinSketch class for strings
  DEFINE_COUNT_MIN_SKETCH_METHODS(std::string, "CountMinSketchStr");

  // CountMinSketch class for int
  DEFINE_COUNT_MIN_SKETCH_METHODS(int, "CountMinSketchInt");
}
