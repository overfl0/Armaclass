from pathlib import Path

from Cython.Build import cythonize
from setuptools import setup

this_directory = Path(__file__).parent

setup(
    ext_modules=cythonize(str(this_directory / 'armaclass' / 'parser.py'),
                          language_level=3,
                          annotate=True,
                          ),
)
