#!/usr/bin/python3

import sys
import atheris

# _cbor2 ensures the C library is imported
#with atheris.instrument_imports():
from armaclass.parser import parse

def test_one_input(data: bytes):
    try:
        parse(data)
    except Exception:
        # We're searching for memory corruption, not Python exceptions
        pass

def main():
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
