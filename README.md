# About
This is a Python parser for Arma 3 class definitions such as those appearing inside unrapified mission files.

It's based on [Fusselwurm's arma-class-parser](https://github.com/Fusselwurm/arma-class-parser) that is written
JavaScript.

I grew tired of using it in conjunction with PyExecJS (complicated to set up and needing to patch things up on
Windows) and py2js (too slow to parse even 300KB sqm files) and decided to port the original JavaScript code to
Python.

# Usage
```python
In [1]: import armaclass

In [2]: armaclass.parse('version=12;\n\nclass Moo  {\r\n value = 1; };')
Out[2]: {'Moo': {'value': 1.0}, 'version': 12.0}
```

### Notes
The naming conventions may not match Python's pep8 as I was trying to stay close to the original names to facilitate
porting. Those (internal) names may be changed in the future.

# Contributing
If you feel something is missing or plain wrong, feel free to submit a Pull Request. You are encouraged to submit the
same PR/suggestion to the original [arma-class-parser](https://github.com/Fusselwurm/arma-class-parser) as well.
