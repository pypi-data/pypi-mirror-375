#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com pdfs e imagens
"""
from __future__ import annotations
from convert_stream.enum_libs.modules import (
    DEFAULT_LIB_PDF, DEFAULT_LIB_IMAGE, DEFAULT_LIB_PDF_TO_IMG, DEFAULT_LIB_IMAGE_TO_PDF,
)
from convert_stream.enum_libs.enums import LibPDF, LibImage, LibImageToPdf, LibPdfToImage
from convert_stream.text.string import FindText
from convert_stream.pdf.pdf_page import PageDocumentPdf
from convert_stream.image.img_object import ImageObject, CollectionImages
from convert_stream.pdf.pdf_document import DocumentPdf, CollectionPagePdf
from convert_stream.pdf.image_to_pdf import LibImageToPdf, ConvertImageToPdf
from convert_stream.pdf.pdf_to_image import ConvertPdfToImages
from soup_files import File, Directory, ProgressBarAdapter, ABCProgressBar


class VoidProgressBar(ABCProgressBar):

    def __init__(self):
        super().__init__()

    def set_percent(self, percent: float):
        pass

    def set_text(self, text: str):
        pass


class ImageStream(CollectionImages):

    def __init__(self, images: list[ImageObject] = []) -> None:
        super().__init__(images)

    def add_image_bytes(self, bt: bytes) -> None:
        im = ImageObject.create_from_bytes(bt)
        self.images.append(im)


class PdfStream(object):

    def __init__(
                self, *,
                pbar: ProgressBarAdapter = ProgressBarAdapter(),
                lib_pdf: LibPDF = DEFAULT_LIB_PDF,
                lib_img: LibImage = DEFAULT_LIB_IMAGE,
                lib_img_to_pdf: LibImageToPdf = DEFAULT_LIB_IMAGE_TO_PDF,
                lib_pdf_to_img: LibPdfToImage = DEFAULT_LIB_PDF_TO_IMG,
            ) -> None:
        self.progress: ProgressBarAdapter = pbar
        self.collection_pages: CollectionPagePdf = CollectionPagePdf()
        self.collection_images: CollectionImages = CollectionImages()
        self.collection_images.set_pbar(pbar)
        self.collection_pages.set_pbar(pbar)
        self.lib_pdf: LibPDF = lib_pdf
        self.lib_img: LibImage = lib_img
        self.lib_img_to_pdf: LibImageToPdf = lib_img_to_pdf
        self.lib_pdf_to_img: LibPdfToImage = lib_pdf_to_img
        self.clear()

    @property
    def is_empty(self) -> bool:
        return self.collection_pages.is_null

    def set_land_scape(self):
        self.collection_pages.set_land_scape()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.progress = pbar
        self.collection_pages.set_pbar(pbar)

    def clear(self):
        self.collection_pages.clear()
        self.collection_images.clear()

    def add_page(self, page: PageDocumentPdf) -> None:
        self.collection_pages.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]) -> None:
        self.collection_pages.add_pages(pages)

    def add_file_image(self, f: File) -> None:
        self.collection_images.add_file_image(f)

    def add_files_image(self, files: list[File]) -> None:
        self.collection_images.add_files_image(files)

    def add_image(self, image: ImageObject) -> None:
        self.collection_images.add_image(image)

    def add_images(self, images: list[ImageObject]) -> None:
        self.collection_images.add_images(images)

    def add_file_pdf(self, f: File) -> None:
        self.collection_pages.add_file_pdf(f)

    def add_files_pdf(self, files: list[File]) -> None:
        self.collection_pages.add_files_pdf(files)

    def add_document(self, doc: DocumentPdf) -> None:
        self.collection_pages.add_document(doc)

    def add_directory_pdf(self, src_dir: Directory, max_files: int = 4000) -> None:
        self.collection_pages.add_directory_pdf(src_dir, max_files=max_files)

    def add_directory_image(self, src_dir: Directory, max_files: int = 4000) -> None:
        self.collection_images.add_directory_images(src_dir, max_files=max_files)

    def to_document(self) -> DocumentPdf:
        if self.collection_pages.is_null and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')
        _doc = None
        if not self.collection_pages.is_null:
            _doc = DocumentPdf.create_from_pages(self.collection_pages.pages)
        if not self.collection_images.is_empty:
            _convert_img_to_pdf = ConvertImageToPdf(self.collection_images)
            _pages = _convert_img_to_pdf.to_document().to_pages()
            self.collection_images.clear()
            if _doc is None:
                _doc = DocumentPdf.create_from_pages(_pages)
            else:
                _doc.add_pages(_pages)
        return _doc

    def to_files_images(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                land_scape: bool = False,
                dpi: int = 300,
            ) -> None:
        if self.collection_pages.is_null and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')
        self.progress.start()
        if not self.collection_pages.is_null:
            self.progress.update_text('Processando Imagens')
            # Criar um documento a partir das páginas
            doc_pdf = DocumentPdf.create_from_pages(self.collection_pages.pages)
            convert_pdf_to_img = ConvertPdfToImages.create(doc_pdf)
            # Converter as páginas PDF em imagens e adicionar a coleção já existe de imagens.
            self.collection_images.add_images(convert_pdf_to_img.to_images(dpi=dpi))
            self.collection_pages.clear()
        # Exportar para arquivos.
        self.collection_images.to_files_image(output_dir, replace=replace, land_scape=land_scape)
        self.progress.stop()

    def to_files_pdf(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                land_scape: bool = False,
            ) -> None:
        if self.collection_pages.is_null and self.collection_images.is_empty:
            raise ValueError('Adicione imagens e/ou documentos para prosseguir!')
        if not self.collection_pages.is_null:
            convert_img_to_pdf = ConvertImageToPdf(self.collection_images)
            self.collection_pages.add_pages(convert_img_to_pdf.to_document().to_pages())
            self.collection_images.clear()
        if land_scape:
            self.collection_pages.set_land_scape()
        self.collection_pages.to_files_pdf(output_dir, replace=replace)


class SplitPdf(object):

    def __init__(self, pages: list[PageDocumentPdf], pbar: ProgressBarAdapter = ProgressBarAdapter()):
        self.pbar: ProgressBarAdapter = pbar
        self.__collection_pages: CollectionPagePdf = CollectionPagePdf(pages)
        self.__collection_pages.set_pbar(self.pbar)

    def is_empty(self) -> bool:
        return self.__collection_pages.is_null

    def export(self, output_dir: Directory, *, replace: bool = False, prefix: str = 'pag') -> None:
        if self.is_empty():
            self.pbar.update_text(f'O Documento está vazio!')
            return
        self.__collection_pages.to_files_pdf(output_dir, replace=replace, prefix=prefix)
        self.__collection_pages.clear()



