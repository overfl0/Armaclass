import pytest

from armaclass import parse, ParseError


def test_class_with_translation_strings():
    expected = {
        'testClass': {
            'title': "Test Class",
            'values': [0, 1],
            'texts': ["STR_UNTRANSLATED", "Translated text"],
            'default': 1
        }
    }
    translations = {
        'STR_CLASS_TITLE': 'Test Class',
        'STR_TRANSLATED': 'Translated text'
    }
    result = parse('''
        class testClass {
            title = $STR_CLASS_TITLE;
            values[] = {0,1};
            texts[] = {$STR_UNTRANSLATED, $STR_TRANSLATED};
            default = 1;
        };
    ''', translations=translations)
    assert result == expected


def test_whitespace_after_translation_key():
    expected = {
        'testClass': {
            'title': 'Translated title',
            'texts': ['Translated text'],
        }
    }
    translations = {
        'STR_CLASS_TITLE': 'Translated title',
        'STR_CLASS_TEXT': 'Translated text'
    }
    result = parse('''
        class testClass {
            title = $STR_CLASS_TITLE ;
            texts[] = {$STR_CLASS_TEXT };};
    ''', translations=translations)
    assert result == expected


def test_whitespace_in_translation_key_property():
    translations = {
        'STR_CLASS_TITLE': 'Translated title',
        'STR_CLASS_TEXT': 'Translated text'
    }
    with pytest.raises(ParseError, match=r'Syntax error'):
        parse('''
            class testClass {
                title = $STR_CLA SS_TITLE;
                texts[] = {$STR_CLASS_TEXT};};
        ''', translations=translations)


def test_whitespace_in_translation_key_array():
    translations = {
        'STR_CLASS_TITLE': 'Translated title',
        'STR_CLASS_TEXT': 'Translated text'
    }
    with pytest.raises(ParseError, match=r'Syntax error'):
        parse('''
            class testClass {
                title = $STR_CLASS_TITLE;
                texts[] = {$STR_CLA SS_TEXT};};
        ''', translations=translations)


def test_eof_in_translation_key():
    translations = {
        'STR_CLASS_TITLE': 'Translated title',
        'STR_CLASS_TEXT': 'Translated text'
    }
    with pytest.raises(ParseError, match=r'Syntax error'):
        parse('''
            class testClass {
                title = $STR_CLASS_TITLE;
                texts[] = {$STR_CLA''', translations=translations)
