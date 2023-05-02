import os

from setuptools import setup, Extension
from Cython.Build import cythonize

# read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


with open(os.path.join(this_directory, 'armaclass', 'parser_template.pyx')) as f:
    contents = f.read()

    with open(os.path.join(this_directory, 'armaclass', 'parser_ucs1.pyx'), 'w') as fw:
        fw.write(contents.replace('UCS_TYPE', 'UCS1'))

    with open(os.path.join(this_directory, 'armaclass', 'parser_ucs2.pyx'), 'w') as fw:
        fw.write(contents.replace('UCS_TYPE', 'UCS2'))

    with open(os.path.join(this_directory, 'armaclass', 'parser_ucs4.pyx'), 'w') as fw:
        fw.write(contents.replace('UCS_TYPE', 'UCS4'))


extensions = [
    Extension('armaclass.parser', [os.path.join('armaclass', 'parser.pyx')]),
    Extension('armaclass.parser_ucs1', [os.path.join('armaclass', 'parser_ucs1.pyx')]),
    Extension('armaclass.parser_ucs2', [os.path.join('armaclass', 'parser_ucs2.pyx')]),
    Extension('armaclass.parser_ucs4', [os.path.join('armaclass', 'parser_ucs4.pyx')]),
]


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

        'License :: OSI Approved :: MIT License',
    ],
    ext_modules=cythonize(extensions,
                          compiler_directives={'language_level': '3'},
                          annotate=True),
)

# Install in "editable mode" for development:
# pip install -e .
