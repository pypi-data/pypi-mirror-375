#!/usr/bin/env python3

from __future__ import annotations
from abc import ABC, abstractmethod
from soup_files import (
    File, Directory, ProgressBarAdapter, CreatePbar,
    InputFiles, LibraryDocs, JsonConvert, JsonData
)
from convert_stream.enum_libs.enums import ColumnsTable
from convert_stream.text.string import FindText, ArrayString, MapText
from convert_stream.pdf.pdf_document import SearchableTextPdf, DocumentPdf
from convert_stream.doc_stream import PdfStream, CollectionPagePdf
import pandas as pd


class ABCTableFiles(ABC):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        self.pbar: ProgressBarAdapter = pbar
        self.files: list[File] = []

    @abstractmethod
    def add_file(self, file: File):
        pass

    @abstractmethod
    def to_data(self) -> pd.DataFrame:
        pass


def get_void_map_table() -> MapText:
    """

    @rtype: MapText
    """
    _map = MapText(
        [],
        col_num_line=ColumnsTable.NUM_LINHA.value,
        col_text=ColumnsTable.TEXT.value,
    )
    _map.add_column(ColumnsTable.NUM_PAGE.value, [])
    _map.add_column(ColumnsTable.FILENAME.value, [])
    _map.add_column(ColumnsTable.FILETYPE.value, [])
    _map.add_column(ColumnsTable.FILE.value, [])
    _map.add_column(ColumnsTable.DIR.value, [])
    return _map


def get_void_df() -> pd.DataFrame:
    """
        Retorna um DataFrame() vazio, apenas com as colunas formatadas
    para tabela de arquivos.
    @rtype: pd.DataFrame
    """
    return get_void_map_table().to_data()


def create_map_from_values(file: File, values: list[str]) -> MapText:
    """

    @rtype: pd.DataFrame
    """
    if len(values) < 1:
        return get_void_map_table()
    _map = MapText(
            values,
            col_text=ColumnsTable.TEXT.value,
            col_num_line=ColumnsTable.NUM_LINHA.value,
    )
    max_num = _map.length
    _map.add_column(ColumnsTable.FILENAME.value, [file.basename()] * max_num)
    _map.add_column(ColumnsTable.FILETYPE.value, [file.extension()] * max_num)
    _map.add_column(ColumnsTable.FILE.value, [file.absolute()] * max_num)
    _map.add_column(ColumnsTable.DIR.value, [file.dirname()] * max_num)
    return _map


def create_df_from_file_pdf(file: File, pbar: ProgressBarAdapter = CreatePbar().get()) -> pd.DataFrame:
    pbar.start()
    items: list[MapText] = []
    doc = PdfStream()
    doc.add_file_pdf(file)
    pages_pdf = doc.to_document().to_pages()
    max_num = len(pages_pdf)
    for num, page in enumerate(pages_pdf):
        pbar.update(
            ((num+1) / max_num) * 100,
            f'Lendo página: [{num+1} / {max_num}]'
        )
        
        text_page: str = page.to_string()
        try:
            if text_page == 'nas':
                mp = create_map_from_values(file, ['-'])
            else:
                mp = create_map_from_values(file, text_page.split('\n'))
        except Exception as e:
            print(e)
        else:
            max_num = mp.length
            mp.add_column(ColumnsTable.NUM_PAGE.value, [f'{page.number_page}'] * max_num)
            items.append(mp)

    doc.clear()
    del doc
    pbar.stop()
    dfs = []
    for m in items:
        dfs.append(m.to_data())
    items.clear()
    if len(dfs) == 0:
        return pd.DataFrame()
    return pd.concat(dfs)


def get_text_from_file(file: str) -> list[str]:
    try:
        with open(file, 'rt') as f:
            lines = f.readlines()
    except Exception as e:
        print(e)
        return []
    else:
        return lines


def create_map_from_file(file: str) -> MapText:
    m = MapText(
        get_text_from_file(file),
        col_text=ColumnsTable.TEXT.value,
        col_num_line=ColumnsTable.NUM_LINHA.value,
    )
    m.add_column(ColumnsTable.NUM_PAGE.value, [file] * m.length)
    return m


class TableFilesText(ABCTableFiles):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        super().__init__(pbar)

    def add_file(self, file: File) -> None:
        self.files.append(file)

    def to_data(self) -> pd.DataFrame:
        values_data: list[pd.DataFrame] = []

        for f in self.files:
            df = create_map_from_file(f.absolute()).to_data()
            if not df.empty:
                values_data.append(df)
        if len(values_data) == 0:
            return get_void_df()
        return pd.concat(values_data)


class TableFilesPdf(ABCTableFiles):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        super().__init__(pbar)

    def add_file(self, file: File) -> None:
        self.files.append(file)

    def add_files_pdf(self, files: list[File]):
        self.files.extend(files)

    def to_data(self) -> pd.DataFrame:
        values_data: list[pd.DataFrame] = []
        max_num = len(self.files)
        self.pbar.start()
        print()
        for num, file in enumerate(self.files):
            self.pbar.update(
                ((num+1)/max_num) * 100,
                f'Gerando tabela do arquivo [{num+1} de {max_num}]'
            )
            df = create_df_from_file_pdf(file)
            if not df.empty:
                values_data.append(df)
        print()
        self.pbar.stop()
        if len(values_data) < 1:
            return get_void_df()
        return pd.concat(values_data)


class FileToTable(object):
    def __init__(self, table: ABCTableFiles):
        self.table: ABCTableFiles = table

    def add_file(self, file: File):
        self.table.add_file(file)

    def add_files(self, files: list[File]):
        for f in files:
            self.add_file(f)

    def to_data(self) -> pd.DataFrame:
        return self.table.to_data()

    @classmethod
    def create_doc_txt(cls) -> FileToTable:
        return cls(TableFilesText())

    @classmethod
    def create_doc_pdf(cls) -> FileToTable:
        return cls(TableFilesPdf())


class PdfFinder(object):
    """
        Classe para Filtrar texto em documentos PDF,
    """

    def __init__(self):
        self.docs_collection: dict[File, DocumentPdf] = {}

    def is_empty(self) -> bool:
        return len(self.docs_collection) == 0

    def clear(self) -> None:
        self.docs_collection.clear()

    def add_file_pdf(self, file: File) -> None:
        if file.is_pdf():
            self.docs_collection[file] = DocumentPdf.create_from_file(file)

    def add_files_pdf(self, files: list[File]) -> None:
        for f in files:
            self.add_file_pdf(f)

    def add_directory_pdf(self, dir_pdf: Directory) -> None:
        files = InputFiles(dir_pdf).get_files(file_type=LibraryDocs.PDF)
        if len(files) > 0:
            self.add_files_pdf(files)

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for file_key in self.docs_collection.keys():
            current_doc: DocumentPdf = self.docs_collection[file_key]
            for page_pdf in current_doc.to_pages():
                text_str_in_page = page_pdf.to_string()
                if (text_str_in_page == 'nas') or (text_str_in_page is None):
                    continue
                try:
                    fd = FindText(text_str_in_page, separator=separator)
                    idx = fd.index(text, iqual=iqual, case=case)
                    if idx is None:
                        continue
                    math_text = fd.get_index(idx)
                except:
                    pass
                else:
                    _searchable.add_line(
                        math_text,
                        num_page=str(page_pdf.number_page),
                        num_line=str(idx + 1),
                        file=file_key.absolute(),
                    )
                    return _searchable
            del current_doc
        return _searchable

    def find_all(
                self, text: str,
                separator: str = '\n',
                iqual: bool = False,
                case: bool = False,
                silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for file_key in self.docs_collection.keys():
            current_doc: DocumentPdf = self.docs_collection[file_key]
            for page_pdf in current_doc.to_pages():
                text_str_in_page = page_pdf.to_string()
                if (text_str_in_page == 'nas') or (text_str_in_page is None):
                    continue
                try:
                    _values = text_str_in_page.split(separator)
                    for num, item in enumerate(_values):
                        if case:
                            if iqual:
                                if text == item:
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                            else:
                                if text in item:
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                        else:
                            if iqual:
                                if text.lower() == item.lower():
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                            else:
                                if text.lower() in item.lower():
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                except Exception as e:
                    print(f'{__class__.__name__} {e}')
        return _searchable
