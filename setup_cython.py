import os

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(os.path.join('armaclass', 'parser.py'),
                          language_level=3,
                          annotate=True,
                          ),
)
