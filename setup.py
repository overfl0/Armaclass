from setuptools import setup

setup(
    name='armaclass',
    version='0.2',
    packages=['armaclass'],
    url='https://github.com/overfl0/Armaclass',
    license='MIT',
    author='Lukasz Taczuk',
    author_email='',
    description='Python parser for Arma class definitions (e.g. sqm files)',
    keywords='arma pbo sqm class parser',

    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        'License :: OSI Approved :: MIT License',
    ],
)

# Install in "editable mode" for development:
# pip install -e .
