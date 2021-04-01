import textwrap

from .generator import Generator


class ArmaGenerator(Generator):
    def generate_bool(self, name, data):
        if name is None:  # We're in an array, we don't have a name. Don't print a newline at the end
            return 'true' if data else 'false'

        return '{}={};\n'.format(name, 'true' if data else 'false')

    def generate_float(self, name, data):
        if name is None:  # We're in an array, we don't have a name. Don't print a newline at the end
            return '{}'.format(data)

        return '{}={};\n'.format(name, data)

    def generate_int(self, name, data):
        if name is None:  # We're in an array, we don't have a name. Don't print a newline at the end
            return '{}'.format(data)

        return '{}={};\n'.format(name, data)

    def generate_class(self, name, data):
        inner = [self.generate_item(key, val) for key, val in data.items()]
        template = textwrap.dedent('''\
            class {name}
            {{
            {contents}}};
            ''')

        retval = template.format(name=name, contents=self._indent(''.join(inner)))
        return retval

    def generate_array(self, name, data):
        inner = [self.generate_item(None, val) for val in data]
        template_regular = textwrap.dedent('''\
            {name}[]=
            {{
            {contents}
            }};
            ''')

        template_inner = '{{{contents}}}'

        template = template_inner if name is None else template_regular
        indent = self._noindent if name is None else self._indent

        retval = template.format(name=name, contents=indent(', '.join(inner)))
        return retval

    def _escape_string(self, data):
        return data.replace('"', '""')

    def generate_string(self, name, data):
        if name is None:  # We're in an array, we don't have a name. Don't print a newline at the end
            return '"{}"'.format(self._escape_string(data))

        return '{}="{}";\n'.format(name, self._escape_string(data))


def generate(data, **kwargs):
    g = ArmaGenerator(**kwargs)
    return g.generate(data)
