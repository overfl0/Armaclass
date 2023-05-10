import json
import lzma
import os
import time
from itertools import zip_longest

import armaclass

CONFIG_CPP = os.path.join('config_data', 'config.cpp')
CONFIG_JSON = os.path.join('config_data', 'config.json')

if not os.path.exists(CONFIG_CPP):
    data = lzma.open(CONFIG_CPP + '.xz').read()
    with open(CONFIG_CPP, 'wb') as f:
        f.write(data)

if not os.path.exists(CONFIG_JSON):
    data = lzma.open(CONFIG_JSON + '.xz').read()
    with open(CONFIG_JSON, 'wb') as f:
        f.write(data)


with open(CONFIG_CPP, 'rb') as f:
    print('Reading file...')
    try:
        contents = f.read()
        # contents_s = contents.decode('utf8', errors='surrogateescape')
        contents_s = contents

    except UnicodeDecodeError as ex:
        before = contents[:ex.start]
        lines = before.count(b'\n') + 1
        previous_lines, previous_chars = before.rsplit(b'\n', maxsplit=1)
        charno = ex.start - len(previous_lines)
        last_line, _ = contents[len(previous_lines) + 1:].split(b'\n', maxsplit=1)

        print(f'Error ar line: {lines}, position: {charno}')
        print(last_line)
        print(f'{" " * len(repr(previous_chars))}^^^')
        raise


import pstats, cProfile

# import pyximport
# pyximport.install()

print('Parsing...')
start = time.time()

parsed = armaclass.parse(contents_s)
# cProfile.runctx("parsed = armaclass.parse(contents_s)", globals(), locals(), "Profile.prof")
# s = pstats.Stats("Profile.prof")
# s.strip_dirs().sort_stats("time").print_stats()

stop = time.time()
print(f'Took: {stop - start:.4f}s')


# for _ in range(1000):
#     print('Parsing...')
#     start = time.time()
#     parsed = armaclass.parse(contents_s)
#     stop = time.time()
#     print(f'Took: {stop - start:.4f}s')

# with open(CONFIG_JSON, 'w') as f:
#     json.dump(parsed, fp=f, indent=4)

with open(CONFIG_JSON, 'r') as f:
    model_json = f.read()
    model = json.loads(model_json)


def convert_bytes(obj):
    if type(obj) == bytes:
        return obj.decode('utf-8')
    raise TypeError(f'Cannot serialize type {type(obj)}')


def compare_dicts_equal(model, current, path=''):
    for (key_model, val_model), (key_current, val_current) in zip_longest(model.items(), current.items()):
        if isinstance(key_current, bytes):
            key_current = key_current.decode('utf-8')

        if key_model != key_current:
            error = f'{path}.{key_current} does not match {key_model}'
            raise ValueError(error)

        if isinstance(val_current, bytes):
            val_current = val_current.decode('utf-8')

        if type(val_model) != type(val_current):
            error = f'type({path}.{key_current}) == {type(val_current)} instead of {type(val_model)}'
            raise ValueError(error)

        if type(val_model) == dict:
            compare_dicts_equal(val_model, val_current, f'{path}.{key_model}')

        elif type(val_model) == list:
            compare_lists_equal(val_model, val_current, f'{path}.{key_model}')

        elif val_model != val_current:
            error = f'{path}.{key_current} == {val_current} instead of {val_model}'
            raise ValueError(error)


def compare_lists_equal(model, current, path=''):
    for i, (item_model, item_current) in enumerate(zip_longest(model, current)):
        if isinstance(item_current, bytes):
            item_current = item_current.decode('utf-8')

        if type(item_model) != type(item_current):
            error = f'type({path}[{i}]) == {type(item_current)} instead of {type(item_model)}'
            raise ValueError(error)

        if type(item_model) == dict:
            compare_dicts_equal(item_model, item_current, f'{path}[{i}]')

        elif type(item_model) == list:
            compare_lists_equal(item_model, item_current, f'{path}[{i}]')

        elif item_model != item_current:
            error = f'{path}[{i}] == {item_current} instead of {item_model}'
            raise ValueError(error)

# COMPARE HERE
compare_dicts_equal(model, parsed)
