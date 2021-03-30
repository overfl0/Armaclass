## Status

[![Build Status](https://travis-ci.org/overfl0/Armaclass.svg?branch=master)](https://travis-ci.org/overfl0/Armaclass)

## About
This is a Python parser for Arma 3 class definitions such as those appearing inside unrapified mission files.

It's based on [Fusselwurm's arma-class-parser](https://github.com/Fusselwurm/arma-class-parser) that is written
JavaScript.

I grew tired of using it in conjunction with PyExecJS (complicated to set up and needing to patch things up on
Windows) and py2js (too slow to parse even 300KB sqm files) and decided to port the original JavaScript code to
Python.

## Installation

```
pip install armaclass
```

## Usage
##### Parse the values from a string
```python
In [1]: import armaclass

In [2]: armaclass.parse('version=12;\n\nclass Moo  {\r\n value = 1; };')
Out[2]: {'Moo': {'value': 1.0}, 'version': 12.0}
```

##### Keep the values ordered as they were in the original file
```python
In [3]: armaclass.parse('version=12;\n\nclass Moo  {\r\n value = 1; };', keep_order=True)
Out[3]: OrderedDict([('version', 12.0), ('Moo', OrderedDict([('value', 1.0)]))])
```

Note: Starting with Python 3.7 onwards, dicts are always ordered so it
doesn't matter if you use `keep_order` or not.

##### Generate the files based on a parsed (or manually created) structure
```python
In [4]: from collections import OrderedDict
In [5]: structure = OrderedDict([('version', 12.0), ('Moo', OrderedDict([('value', 1.0)]))])
In [6]: print(armaclass.generate(structure))
version=12;

class Moo
{
    value=1;
};
```

##### Indent with tabs instead of spaces
```python
In [7]: print(armaclass.generate(structure, indent=1, use_tabs=True))
version=12;

class Moo
{
        value=1;
};
```

### Extending the generator
You can use this library to write a program that will port your Arma class files to DayZ, for example.
To do so, you will need to create your own generator by subclassing `armaclass.generator.Generator` and implementing
your own methods (the ones raising `NotImplemented`).

### Notes
The naming conventions may not match Python's pep8 as I was trying to stay close to the original parsing names to
facilitate porting. Those (internal) names may be changed in the future.

## Development
- Create a virtualenv using your preferred method (mkvirtualenv, venv, etc...)
- `pip install -r requirements.txt`
- Write code AND tests
- `pytest` to test run your tests
- `ptw -n` if you want `pytest` to automatically be called whenever
  you save any file from the project

## Contributing
If you feel something is missing or plain wrong, feel free to submit a Pull Request. You are encouraged to submit the
same PR/suggestion to the original [arma-class-parser](https://github.com/Fusselwurm/arma-class-parser) as well.
