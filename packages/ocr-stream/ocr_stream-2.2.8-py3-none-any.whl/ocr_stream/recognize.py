#!/usr/bin/env python3
from __future__ import annotations
from convert_stream import ImageObject, LibImage, DocumentPdf, PageDocumentPdf, ConvertPdfToImages, PdfStream
from ocr_stream.bin_tess import BinTesseract
from ocr_stream.modules import LibOcr, DEFAULT_LIB_OCR, ModuleOcr
from ocr_stream.ocr import TesseractOcr, TextRecognized
from pandas import DataFrame
from soup_files import File, ProgressBarAdapter, CreatePbar


class RecognizeImage(object):
    """
        Reconhecer textos em imagens com pytesseract|pyocr usando o tesseract
    """

    def __init__(
                self,
                bin_tess: BinTesseract = BinTesseract(), *,
                lib_ocr: LibOcr = DEFAULT_LIB_OCR
            ):
        super().__init__()
        self.module_ocr: TesseractOcr = TesseractOcr.create(
            bin_tess,
            lib_ocr=lib_ocr,
            lang=bin_tess.get_lang(),
            tess_data_dir=bin_tess.get_tessdata_dir(),
        )

    @property
    def bin_tesseract(self) -> BinTesseract:
        return self.module_ocr.mod_ocr.bin_tess

    def image_content_data(self, img: ImageObject | File) -> DataFrame:
        """
        Retorna uma tabela estruturada com os dados reconhecidos da imagem.

        Este método extrai as informações contidas em uma imagem e as organiza em
        um DataFrame com colunas como o texto detectado, coordenadas da caixa delimitadora,
        nível do OCR e confiabilidade, entre outras.

        Parâmetros:
        img (ImageObject | File): A imagem a ser processada, podendo ser um objeto
        `ImageObject` ou um arquivo `File`.

        Retorna:
        DataFrame: Uma tabela contendo os dados reconhecidos na imagem.

        Lança:
        ValueError: Se o tipo do parâmetro `img` não for `ImageObject` ou `File`.

        @param img: Imagem a ser processada, podendo ser uma instância de `ImageObject`
            ou um arquivo `File`.
        @type img: ImageObject | File

        @rtype: pandas.DataFrame
        @return: Um DataFrame com os dados reconhecidos na imagem.

        @raise ValueError: Caso o tipo de `img` não seja `ImageObject` nem `File`.
        """
        return self.image_recognize(img).to_dataframe()

    def image_recognize(self, img: ImageObject | File) -> TextRecognized:
        rec: TextRecognized = self.module_ocr.to_reconize(img)
        return rec

    def image_to_string(self, img: ImageObject | File) -> str:
        return self.module_ocr.to_string(img)


class RecognizePdf(object):

    def __init__(
                self,
                bin_tess: BinTesseract = BinTesseract(), *,
                lib_ocr: LibOcr = DEFAULT_LIB_OCR,
            ):
        self.recognize_image: RecognizeImage = RecognizeImage(bin_tess, lib_ocr=lib_ocr)
        self.pbar: ProgressBarAdapter = CreatePbar().get()

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p

    def recognize_page_pdf(self, page: PageDocumentPdf, *, dpi: int = 350) -> DocumentPdf:
        """
            Converte a página em Imagem, reconhece o texto com OCR e
        retorna uma nova página com o texto reconhecido.
        """
        _doc = DocumentPdf.create_from_pages([page])
        _conv = ConvertPdfToImages.create(_doc)
        img: ImageObject = _conv.to_images(dpi=dpi)[0]
        text_recognized: TextRecognized = self.recognize_image.image_recognize(img)
        del _doc
        del _conv
        del img
        return text_recognized.to_document()

    def recognize_document(self, doc: DocumentPdf, *, dpi: int = 350) -> DocumentPdf:
        _pages: list[PageDocumentPdf] = []
        _pages.clear()
        _conv = ConvertPdfToImages.create(doc)
        images: list[ImageObject] = _conv.to_images(dpi=dpi)
        max_num: int = len(images)
        for num, img in enumerate(images):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Aplicando OCR [{num+1} de {max_num}]'
            )
            text_recognized = self.recognize_image.image_recognize(img)
            _pages.append(text_recognized.to_page_pdf())
        print()
        self.pbar.stop()
        new_doc = DocumentPdf.create_from_pages(_pages)
        return new_doc

    def recognize_file_pdf(self, file: File, *, dpi: int = 300) -> DocumentPdf:
        file_doc = DocumentPdf.create_from_file(file)
        recognized_doc = self.recognize_document(file_doc, dpi=dpi)
        del file_doc
        return recognized_doc

