#!/usr/bin/env python3
from __future__ import annotations
from io import BytesIO
from typing import Union
from soup_files import File, Directory, LibraryDocs, InputFiles

from ._version import (
    __module_name__, __author__, __license__, __modify_date__, __version__
)
from convert_stream.enum_libs.enums import *
from convert_stream.enum_libs.modules import (
    LibPDF, LibDate, LibImage, LibPdfToImage, LibImageToPdf,
    DEFAULT_LIB_PDF, DEFAULT_LIB_IMAGE, DEFAULT_LIB_PDF_TO_IMG,
    DEFAULT_LIB_IMAGE_TO_PDF, ModPdfToImage, ModPagePdf, ModuleImage,
    ModImageToPdf, MOD_FITZ, MOD_PYPDF, MOD_CANVAS, MOD_IMG_PIL, MOD_IMG_OPENCV,
)
from .text.terminal import print_title, print_line
from .text.string import (
    FindText, ArrayString, MapText
)
from .text.date import ConvertStringDate
from convert_stream.image.img_object import (
    ImageObject, Image, MatLike, get_hash_from_bytes, CollectionImages,
)
from convert_stream.pdf import (
    PageDocumentPdf, DocumentPdf, ConvertImageToPdf, ConvertPdfToImages,
    ModImageToPdf, ModDocPdf, CollectionPagePdf, DEFAULT_LIB_PDF,
    DEFAULT_LIB_IMAGE_TO_PDF, DEFAULT_LIB_PDF_TO_IMG
)
from .doc_stream import PdfStream, SplitPdf
from .sheets import save_data, ReadFileSheet
from .table_files import (
    get_void_df, create_df_from_file_pdf, create_map_from_values,
    FileToTable, ColumnsTable, PdfFinder, SearchableTextPdf
)


def __create_stream() -> PdfStream:
    st = PdfStream()
    st.clear()
    return st


def read_pdf(file: Union[str, File, bytes, BytesIO]) -> PdfStream:
    _pdf_stream = __create_stream()

    if isinstance(file, File):
        _pdf_stream.add_file_pdf(file)
    elif isinstance(file, str):
        _pdf_stream.add_file_pdf(File(file))
    elif isinstance(file, bytes):
        _pdf_stream.add_document(DocumentPdf(BytesIO(file)))
    elif isinstance(file, BytesIO):
        _pdf_stream.add_document(DocumentPdf(file))
    else:
        raise ValueError()
    return _pdf_stream


def read_files_pdf(files: Union[list[str], list[File]]) -> PdfStream:
    _pdf_stream = __create_stream()
    if len(files) == 0:
        return _pdf_stream

    if isinstance(files[0], str):
        for f in files:
            _pdf_stream.add_file_pdf(File(f))
    elif isinstance(files[0], File):
        _pdf_stream.add_files_pdf(files)
    else:
        raise ValueError()
    return _pdf_stream


def read_image(image: Union[str, File, bytes, BytesIO]) -> PdfStream:
    _pdf_stream = __create_stream()
    if isinstance(image, str):
        _pdf_stream.add_file_image(File(image))
    elif isinstance(image, File):
        _pdf_stream.add_image(ImageObject.create_from_file(image))
    elif isinstance(image, bytes):
        _pdf_stream.add_image(ImageObject.create_from_bytes(image))
    elif isinstance(image, BytesIO):
        image.seek(0)
        _pdf_stream.add_image(ImageObject.create_from_bytes(image.getvalue()))
    else:
        raise ValueError()
    return _pdf_stream


