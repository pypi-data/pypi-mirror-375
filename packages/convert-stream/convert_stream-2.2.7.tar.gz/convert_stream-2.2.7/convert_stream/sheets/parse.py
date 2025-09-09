#!/usr/bin/env python3
#
from __future__ import annotations
import re


class DataString(object):
    def __init__(self, value: str):
        self.value = value

    def is_null(self) -> bool:
        if (self.value is None) or (self.value == ''):
            return True
        return False

    def to_utf8(self) -> DataString:
        items_for_remove = [
            '\xa0T\x04',
        ]
        try:
            for i in items_for_remove:
                REG = re.compile(i)
                self.value = REG.sub("_", self.value)
        except:
            return self
        else:
            self.value = self.value.encode("utf-8", errors="replace").decode("utf-8")
        return self

    def to_upper(self) -> DataString:
        self.value = self.value.upper()
        return self

    def to_list(self, separator: str = ' ') -> list[str]:
        """
            Transforma uma string em uma lista de strings.
        """
        try:
            return self.value.split(separator)
        except Exception as e:
            print(e)
            return []

    def replace_all(self, char: str, new_char: str = '_') -> DataString:
        """
            Usar expressão regular para substituir caracteres.
        """
        # re.sub(r'{}'.format(char), new_char, text)
        self.value = re.sub(re.escape(char), new_char, self.value)
        return self

    def replace_bad_chars(self, *, new_char='-') -> DataString:
        char_for_remove = [
            ':', ',', ';', '$', '=',
            '!', '}', '{', '(', ')',
            '|', '\\', '‘', '*'
                            '¢', '“', '\'', '¢', '"',
            '#', '<', '?', '>',
            '»', '@', '+', '[', ']',
            '%', '%', '~', '¥', '«',
            '°', '¢', '”', '&'
        ]

        for char in char_for_remove:
            self.replace_all(char, new_char)
        format_chars = [
            '-_', '_-', '--', '__',
        ]
        for c in format_chars:
            self.replace_all(c)
        return self
