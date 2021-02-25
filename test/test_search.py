import unittest

from armaclass import parse, search


class TestArmaClass(unittest.TestCase):

    def test_get_value(self):
        expected = 1
        result = parse('class Moo { value=1;};')
        self.assertEqual(search(result, "Moo>>value"), expected)

    def test_invalid_path(self):
        expected = None
        result = parse('class Moo { value=1;};')
        self.assertEqual(search(result, "Moo>>bar"), expected)

    def test_get_class(self):
        expected = {'value': 1}
        data = parse('class Moo { class Foo { value = 1;}; };')
        result = search(data, "Moo>>Foo")
        self.assertEqual(result, expected)

    def test_get_class_value(self):
        expected = 1
        data = parse('class Moo { class Foo { value = 1;}; };')
        result = search(data, "Moo>>Foo>>value")
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
