from .generator import Generator


class ArmaGenerator(Generator):
    def generate_float(self, name, data):
        if name is None:
            return '{}'.format(data)

        return '{}={};\n'.format(name, data)

    def generate_int(self, name, data):
        if name is None:
            return '{}'.format(data)

        return '{}={};\n'.format(name, data)

    def generate_class(self, name, data):
        inner = [self.generate_item(key, val) for key, val in data.items()]

        retval = 'class {}\n{{\n{}}};\n'.format(name, self._indent(''.join(inner)))
        return retval

    def generate_array(self, name, data):
        inner = [self.generate_item(None, val) for val in data]

        retval = '{}[]=\n{{\n{}\n}};\n'.format(name, self._indent(','.join(inner)))
        return retval

    def _escape_string(self, data):
        return data.replace('"', '""')

    def generate_string(self, name, data):
        if name is None:
            return '"{}"'.format(self._escape_string(data))

        return '{}="{}";\n'.format(name, self._escape_string(data))
