#include <pybind11/pybind11.h>
#include "dynaplex/hello.h"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "dynaplex hybrid C++ core";
    m.def("hello", []() { return dynaplex::hello(); }, "Return a friendly greeting");

	m.def("goodbye", []() { return dynaplex::goodbye(); }, "Return a friendly farewell");
}
