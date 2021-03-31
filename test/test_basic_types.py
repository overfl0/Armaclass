import pytest

from armaclass import parse


def test_empty():
    expected = {}
    result = parse('')
    assert result == expected


def test_string():
    expected = {'var': 'foo'}
    result = parse('var="foo";')
    assert result == expected
    assert type(result['var']) == str


def test_unquoted_string():
    expected = {'var': 'foo'}
    result = parse('var= foo ;')
    assert result == expected
    assert type(result['var']) == str


def test_unquoted_string_with_dot():
    expected = {'var': 'fo.o'}
    result = parse('var= fo.o ;')
    assert result == expected
    assert type(result['var']) == str


@pytest.mark.parametrize('sqf, python', [
    ('12.3', 12.3),
    ('-12.3', -12.3),
    ('+12.3', 12.3),
    ('0.0', 0.0),
])
def test_float(sqf, python):
    expected = {'var': python}
    result = parse('var={};'.format(sqf))
    assert result == expected
    assert type(result['var']) == float


@pytest.mark.parametrize('sqf, python', [
    ('12', 12),
    ('-12', -12),
    ('+12', 12),
    ('0', 0),
])
def test_int(sqf, python):
    expected = {'var': python}
    result = parse('var={};'.format(sqf))
    assert result == expected
    assert type(result['var']) == int


@pytest.mark.parametrize('sqf, python', [
    ('false', False),
    ('False', False),
    ('FaLsE', False),
    ('true', True),
    ('True', True),
    ('TrUe', True),
])
def test_bool(sqf, python):
    expected = {'var': python}
    result = parse('var={};'.format(sqf))
    assert result == expected
    assert type(result['var']) == bool


def test_class():
    expected = {'var': {}}
    result = parse('class var {};')
    assert result == expected
    assert type(result['var']) == dict


def test_empty_array():
    expected = {'var': []}
    result = parse('var[]={};')
    assert result == expected
    assert type(result['var']) == list


def test_array():
    expected = {'var': [1, 2, 3]}
    result = parse('var[]={1, 2, 3};')
    assert result == expected
    assert type(result['var']) == list
