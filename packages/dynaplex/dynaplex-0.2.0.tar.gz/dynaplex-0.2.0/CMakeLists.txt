cmake_minimum_required(VERSION 3.21)
project(dynaplex LANGUAGES CXX)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 CONFIG REQUIRED)

# Create the Python extension module named exactly "_core"
pybind11_add_module(_core
  src/bindings.cpp
  src/hello.cpp
)

target_include_directories(_core PRIVATE include)

# Put the compiled extension inside the Python package directory "dynaplex/"
install(TARGETS _core
  LIBRARY DESTINATION dynaplex
  RUNTIME DESTINATION dynaplex
  ARCHIVE DESTINATION dynaplex
)

# Ship the pure-Python files as part of the package
install(FILES
  python/dynaplex/__init__.py
  python/dynaplex/ops.py
  DESTINATION dynaplex
)
