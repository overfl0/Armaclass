import os
import platform
import sys

from setuptools import setup

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

ext_modules = None
if not any(arg in sys.argv for arg in ['clean', 'check']) and \
        'SKIP_CYTHON' not in os.environ and \
        platform.python_implementation() == 'CPython':
    try:
        from Cython.Build import cythonize
    except ImportError:
        pass
    else:
        compiler_directives = {}
        if 'CYTHON_TRACE' in sys.argv:
            compiler_directives['linetrace'] = True

        ext_modules = cythonize(
            os.path.join('armaclass', 'parser.py'),
            language_level=3,
            compiler_directives=compiler_directives,
        )

setup(
    name='armaclass',
    version='0.2.3',
    packages=['armaclass'],
    url='https://github.com/overfl0/Armaclass',
    license='MIT',
    author='Lukasz Taczuk',
    author_email='',
    description='Python parser and generator for Arma class definitions (e.g. sqm files)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='arma pbo sqm class parser generator',
    python_requires='>=3.7',

    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

        'License :: OSI Approved :: MIT License',
    ],
    ext_modules=ext_modules,
)

# Install in "editable mode" for development:
# pip install -e .
