from setuptools import setup
from Cython.Build import cythonize
import numpy

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#multiple-cython-files-in-a-package
# Run the following from </path/to/siuru>/code to compile components:
# python setup.py build_ext --inplace

setup(
    name="SIURU",
    ext_modules=cythonize(
        ["dataloaders/*.py",
        "preprocessors/*.py",
        "encoders/*.py",
        "models/*.py"]
    ),
    include_path = [numpy.get_include()]
)
