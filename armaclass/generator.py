import textwrap


class Generator:
    # Implement the following methods for your own generator
    def generate_number(self, name, data):
        if data == int(data):
            return self.generate_int(name, int(data))
        return self.generate_float(name, data)

    def generate_float(self, name, data):
        raise NotImplemented

    def generate_int(self, name, data):
        raise NotImplemented

    def generate_class(self, name, data):
        raise NotImplemented

    def generate_array(self, name, data):
        raise NotImplemented

    def generate_string(self, name, data):
        raise NotImplemented

    # ============================================

    def __init__(self, indent=4, indent_character=' '):
        self.indent_value = indent
        self.indent_character = indent_character

    def _indent(self, text):
        return textwrap.indent(text, self.indent_character * self.indent_value)

    # =============================================

    def generate_item(self, name, data):
        item_type = type(data)
        # print(item_type)

        if issubclass(item_type, (float, int)):
            text = self.generate_number(name, data)
        elif issubclass(item_type, dict):
            text = self.generate_class(name, data)
        elif issubclass(item_type, (list, tuple)):
            text = self.generate_array(name, data)
        elif issubclass(item_type, str):
            text = self.generate_string(name, data)
        else:
            raise Exception('Can\'t handle item type: {}'.format(item_type))
        # print(text, end='')

        return text

    def generate(self, data):
        text_items = []
        for key, val in data.items():
            text_items.append(self.generate_item(key, val))

        return '\n'.join(text_items)
