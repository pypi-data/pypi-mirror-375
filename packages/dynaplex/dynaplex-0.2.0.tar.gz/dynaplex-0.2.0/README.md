# DynaPlex


Minimal C++ extension (pybind11 + CMake) packaged as a Python wheel.


## Build (local, tested on Windhoos)

Assumes a python installation (below assumes regular, not Conda python), and a c++ toolchain. 

Create venv:
```bash
python -m venv .venv 
.\.venv\Scripts\activate.bat  
python -m pip install --upgrade pip 
python -m pip install build scikit-build-core pybind11 pytest
```

Build wheels:

```bash
python -m build # creates sdist and wheel in dist/ folder
```

Install the wheel:

```bash
python -m pip install dist/dynaplex-*.whl
```

If the wheel cannot be found (Windows) use this command instead:
```bash
for %f in (dist\dynaplex-*.whl) do python -m pip install --force-reinstall "%f"
```

Run tests:

```bash
pytest -q
```