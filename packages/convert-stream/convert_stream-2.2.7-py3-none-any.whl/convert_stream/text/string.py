#!/usr/bin/env python3
from __future__ import annotations
import pandas as pd


class MapText(object):

    def __init__(
                self,
                elements: list[str], *,
                col_key: str = 'KEY',
                col_num_line: str = 'NUM_LINHA',
                col_text: str = 'TEXTO',
            ) -> None:
        self.col_key: str = col_key
        self.col_num_line: str = col_num_line
        self.col_text: str = col_text
        max_num: int = len(elements)
        self.map_elements: dict[str, list[str]] = {
            self.col_key: [f"{num}" for num in range(0, max_num)],
            self.col_num_line: [f"{x + 1}" for x in range(0, max_num)],
            self.col_text: elements,
        }

    @property
    def is_empty(self) -> bool:
        return len(self.map_elements[self.col_text]) == 0

    @property
    def length(self) -> int:
        return len(self.map_elements[self.col_text])

    @property
    def columns(self) -> list[str]:
        return list(self.map_elements.keys())

    def add_column(self, col: str, values: list[str]) -> None:
        if len(values) != self.length:
            raise ValueError(f'Os valores da coluna {col} precisam ter o tamanho: {self.length}')
        self.map_elements[col] = values

    def to_data(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.map_elements)

    def get_line(self, idx: int, *, separator: str = ' ') -> str | None:
        if self.is_empty:
            return None
        value = ''

        try:
            for _key in self.map_elements.keys():
                value = f'{value}{separator}{self.map_elements[_key][idx]}'
        except:
            return None
        else:
            return value


class ArrayString(object):

    def __init__(self, values: list[str]):
        self.values: list[str] = values

    @property
    def is_null(self) -> bool:
        return len(self.values) == 0

    def contains(self, text: str, iqual: bool = False, case: bool = False) -> bool:
        if iqual:
            for i in self.values:
                if case:
                    if i == text:
                        return True
                else:
                    if text.lower() == i.lower():
                        return True
        else:
            for i in self.values:
                if case:
                    if text in i:
                        return True
                else:
                    if text.lower() in i.lower():
                        return True
        return False

    def get_next(self, text: str, iqual: bool = False, case: bool = False) -> str | None:

        if iqual:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if i == text:
                            return self.values[num+1]
                    else:
                        if text.lower() == i.lower():
                            return self.values[num+1]
            except:
                return None
        else:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if text in i:
                            return self.values[num+1]
                    else:
                        if text.lower() in i.lower():
                            return self.values[num+1]
            except:
                return None
        return None

    def get_back(self, text: str, iqual: bool = False, case: bool = False) -> str | None:

        if iqual:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if i == text:
                            return self.values[num - 1]
                    else:
                        if text.lower() == i.lower():
                            return self.values[num - 1]
            except:
                return None
        else:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if text in i:
                            return self.values[num - 1]
                    else:
                        if text.lower() in i.lower():
                            return self.values[num - 1]
            except:
                return None
        return None

    def get_next_all(self, text: str, iqual: bool = False, case: bool = False) -> list[str]:
        if iqual:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if i == text:
                            return self.values[num:]
                    else:
                        if text.lower() == i.lower():
                            return self.values[num:]
            except:
                return []
        else:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if text in i:
                            return self.values[num:]
                    else:
                        if text.lower() in i.lower():
                            return self.values[num:]
            except:
                return []
        return []

    def get_back_all(self, text: str, iqual: bool = False, case: bool = False) -> list[str]:
        if iqual:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if i == text:
                            return self.values[:num]
                    else:
                        if text.lower() == i.lower():
                            return self.values[:num]
            except:
                return []
        else:
            try:
                for num, i in enumerate(self.values):
                    if case:
                        if text in i:
                            return self.values[:num]
                    else:
                        if text.lower() in i.lower():
                            return self.values[:num]
            except:
                return []
        return []

    def index(self, text: str, *, iqual: bool = False, case: bool = True) -> int | None:
        num_idx = None
        if iqual:
            for idx, i in enumerate(self.values):
                if case:
                    if i == text:
                        num_idx = idx
                        break
                else:
                    if text.lower() == i.lower():
                        num_idx = idx
                        break
        else:
            for idx, i in enumerate(self.values):
                if case:
                    if text in i:
                        num_idx = idx
                        break
                else:
                    if text.lower() in i.lower():
                        num_idx = idx
                        break
        return num_idx

    def get_index(self, num: int) -> str | None:
        try:
            return self.values[num]
        except:
            return None

    def find(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')

        element = None
        if iqual:
            for i in self.values:
                if case:
                    if text == i:
                        element = i
                        break
                else:
                    if text.lower() == i.lower():
                        element = i
                        break
        else:
            for i in self.values:
                if case:
                    if text in i:
                        element = i
                        break
                else:
                    if text.lower() in i.lower():
                        element = i
                        break
        return element

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> list[str]:
        items = []
        if iqual:
            for i in self.values:
                if case:
                    if i == text:
                        items.append(i)
                else:
                    if text.lower() == i.lower():
                        items.append(i)
        else:
            for i in self.values:
                if case:
                    if text in i:
                        items.append(i)
                else:
                    if text.lower() in i.lower():
                        items.append(i)
        return items

    def count(self, text: str, *, iqual: bool = False, case: bool = True) -> int:
        count: int = 0
        if iqual:
            for i in self.values:
                if case:
                    if i == text:
                        count += 1
                else:
                    if text.lower() == i.lower():
                        count += 1
        else:
            for i in self.values:
                if case:
                    if text in i:
                        count += 1
                else:
                    if text.lower() in i.lower():
                        count += 1
        return count


class FindText(object):
    """
        Filtrar palavras/strings em textos longos
    """
    def __init__(self, text_value: str, separator: str = ' '):
        """

        :param text_value: texto bruto a ser filtrado
        :param separator: separador de texto a ser usado durante o filtro
        :type  text_value: str
        :type  separator: str
        :return: None
        """
        self.array: ArrayString = ArrayString(text_value.split(separator))
        self.separator: str = separator

    @property
    def is_null(self) -> bool:
        return self.array.is_null

    def contains_text(self, text: str, *, iqual: bool = False, case: bool = True) -> bool:
        return self.array.contains(text, iqual=iqual, case=case)

    def index(self, text: str, *, iqual: bool = False, case: bool = True) -> int | None:
        num_idx = None
        if iqual:
            for idx, i in enumerate(self.array.values):
                if case:
                    if i == text:
                        num_idx = idx
                        break
                else:
                    if text.lower() == i.lower():
                        num_idx = idx
                        break
        else:
            for idx, i in enumerate(self.array.values):
                if case:
                    if text in i:
                        num_idx = idx
                        break
                else:
                    if text.lower() in i.lower():
                        num_idx = idx
                        break
        return num_idx

    def get_index(self, num: int) -> str | None:
        return self.array.get_index(num)

    def to_array(self) -> ArrayString:
        return ArrayString(self.array.values)

    def find(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find(text, iqual=iqual, case=case)

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> list[str]:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find_all(text, iqual=iqual, case=case)




