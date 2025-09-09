#!/usr/bin/env python3

from enum import Enum


class ColumnsTable(Enum):

    NUM_LINHA = 'NUM_LINHA'
    NUM_PAGE = 'NUM_PÁGINA'
    TEXT = 'TEXTO'
    FILE = 'ARQUIVO'
    FILENAME = 'NOME_ARQUIVO'
    DIR = 'PASTA'
    FILETYPE = 'TIPO_ARQUIVO'

    @classmethod
    def to_list(cls) -> list[str]:
        return [
            cls.NUM_LINHA.value,
            cls.NUM_PAGE.value,
            cls.TEXT.value,
            cls.FILE.value,
            cls.FILENAME.value,
            cls.FILETYPE.value,
            cls.DIR.value,
        ]


class LibPdfToImage(Enum):

    PDF_TO_IMG_FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImageToPdf(Enum):

    IMAGE_TO_PDF_FITZ = 'fitz'
    IMAGE_TO_PDF_CANVAS = 'canvas'
    IMAGE_TO_PDF_PIL = 'pil'
    NOT_IMPLEMENTED = 'null'


class LibPDF(Enum):

    PYPDF = 'pypdf'
    FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImage(Enum):

    PIL = 'pil'
    OPENCV = 'opencv'
    NOT_IMPLEMENTED = 'null'


class LibDate(Enum):
    D_M_Y = '%d-%m-%Y'
    DMY = '%d/%m/%Y'
    dmy = '%d/%m/%y'
    d_m_y = '%d-%m-%y'
    YMD = '%Y/%m/%d'
    Y_M_D = '%Y-%m-%d'


class RotationAngle(Enum):

    ROTATION_90 = 90
    ROTATION_180 = 180
    ROTATION_270 = 270
