import pytest

import armaclass


def test_nested_arrays_generation():
    items = {
        'kickTimeout': [
            [0, -1], [1, 180], [2, 180], [3, 180],
        ]
    }

    output = armaclass.generate(items)
    items_reparsed = armaclass.parse(output)

    assert items == items_reparsed


def _common_test_(python, sqf):
    output = armaclass.generate(python)
    assert output.strip() == sqf

    item_reparsed = armaclass.parse(output)
    assert item_reparsed == python


@pytest.mark.parametrize('python, sqf', [
    ({'var': 'value'}, 'var="value";'),
    ({'var': ['value']}, 'var[]=\n{\n    "value"\n};'),
    ({'var': 'value1\nvalue2\nvalue3'}, 'var="value1" \\n "value2" \\n "value3";'),
    ({'var': '"value1"\n"value2"\nvalue3'}, 'var="""value1""" \\n """value2""" \\n "value3";'),
])
def test_string_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({'var': 12.3}, 'var=12.3;'),
    ({'var': -12.3}, 'var=-12.3;'),
    ({'var': [12.3]}, 'var[]=\n{\n    12.3\n};'),
])
def test_float_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({'var': 12}, 'var=12;'),
    ({'var': -12}, 'var=-12;'),
    ({'var': [12]}, 'var[]=\n{\n    12\n};'),
])
def test_int_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({'var': True}, 'var=true;'),
    ({'var': False}, 'var=false;'),
    ({'var': [True]}, 'var[]=\n{\n    true\n};'),
    ({'var': [False]}, 'var[]=\n{\n    false\n};'),
])
def test_bool_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({'var': {}}, 'class var\n{\n};'),
    ({'var': {'foo': 5}}, 'class var\n{\n    foo=5;\n};'),
])
def test_class_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({'var': [1, 2, 3]}, 'var[]=\n{\n    1, 2, 3\n};'),
])
def test_array_generation(python, sqf):
    _common_test_(python, sqf)


@pytest.mark.parametrize('python, sqf', [
    ({}, ''),
])
def test_empty_input_generation(python, sqf):
    _common_test_(python, sqf)
