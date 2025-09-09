#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from soup_files import Directory, ProgressBarAdapter, CreatePbar
from convert_stream.enum_libs.enums import LibPdfToImage
from convert_stream.enum_libs.modules import DEFAULT_LIB_PDF_TO_IMG, DEFAULT_LIB_IMAGE
from convert_stream.image.img_object import ImageObject, LibImage, CollectionImages
from convert_stream.pdf.pdf_page import PageDocumentPdf
from convert_stream.pdf.pdf_document import DocumentPdf

try:
    import fitz
    MOD_FITZ = True
except ImportError:
    try:
        import pymupdf as fitz
        from pymupdf import Page, Pixmap
        MOD_FITZ = True
    except ImportError:
        fitz = object
        fitz.Page = object
        fitz.TextPage = object


class ABCConvertPdf(ABC):

    def __init__(self, document: DocumentPdf):
        self.document: DocumentPdf = document
        self.lib_pdf_to_image: LibPdfToImage = DEFAULT_LIB_PDF_TO_IMG
        self.pbar: ProgressBarAdapter = CreatePbar().get()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.pbar = pbar

    @abstractmethod
    def to_images(
                self, *,
                dpi: int = 150,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> list[ImageObject]:
        """
            Converte as páginas PDF do documento em lista de objetos imagem ImageObject

        :param dpi: DPI do documento, resolução da renderização.
        :param lib_image: Biblioteca para manipular imagens PIL/OpenCv
        """
        pass

    @abstractmethod
    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            gaussian_filter: bool = False,
            dpi: int = 300,
            lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        """
            Converte todas as páginas do documento em objeto de imagem e salva no disco
        em formato de imagem PNG.
        """
        pass


class ImplementConvertPdfFitz(ABCConvertPdf):

    def __init__(self, document: DocumentPdf):
        super().__init__(document)

    def __get_pages(self) -> list[Page]:
        pages = self.document.to_pages()
        fitz_pages = []
        for p in pages:
            fitz_pages.append(p.implement_page_pdf.mod_page)
        return fitz_pages

    def to_images(
                self, *,
                dpi: int = 200,
                lib_image: LibImage = DEFAULT_LIB_IMAGE
            ) -> list[ImageObject]:
        images: list[ImageObject] = []
        pages_fitz: list[Page] = self.__get_pages()
        _count = len(pages_fitz)
        print()
        for n, pg in enumerate(pages_fitz):
            self.pbar.update(
                ((n+1)/_count) * 100,
                f'Convetendo: {n+1} de {_count}'
            )
            pix: Pixmap = pg.get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes('png', jpg_quality=100),
                lib_image=LibImage.PIL,
            )
            images.append(img)
        print()
        return images

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                gaussian_filter: bool = False,
                dpi: int = 300,
                lib_image: LibImage = DEFAULT_LIB_IMAGE
            ) -> None:
        pages_fitz: list[Page] = self.__get_pages()
        _count = len(pages_fitz)
        print()
        for n, pg in enumerate(pages_fitz):
            self.pbar.update(
                ((n + 1) / _count) * 100,
                f'Exportando: {n + 1} de {_count}'
            )
            out_file = output_dir.join_file(f'pag-{n+1}.png')
            if not replace:
                if out_file.exists():
                    self.pbar.update_text(f'Pulando: {out_file.basename()}')
                    continue
            pix: Pixmap = pg.get_pixmap(dpi=dpi)
            img = ImageObject.create_from_bytes(
                pix.tobytes('png', jpg_quality=100),
                lib_image=LibImage.PIL,
            )
            img.to_file(out_file)
        print()


class ConvertPdfToImages(object):

    def __init__(self, mod_convert_to_image: ABCConvertPdf):
        self.mod_convert_to_image: ABCConvertPdf = mod_convert_to_image

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.mod_convert_to_image.set_pbar(pbar)

    def to_images(
                self, *, dpi: int = 300, lib_image: LibImage = DEFAULT_LIB_IMAGE
            ) -> list[ImageObject]:
        return self.mod_convert_to_image.to_images(dpi=dpi, lib_image=lib_image)

    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            gaussian_filter: bool = False,
            dpi: int = 300,
            lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        self.mod_convert_to_image.to_files_image(
            dpi=dpi,
            lib_image=lib_image,
            replace=replace,
            output_dir=output_dir,
            gaussian_filter=gaussian_filter
        )

    @classmethod
    def create(cls, doc: DocumentPdf) -> ConvertPdfToImages:
        _mod = ImplementConvertPdfFitz(doc)
        return cls(_mod)

