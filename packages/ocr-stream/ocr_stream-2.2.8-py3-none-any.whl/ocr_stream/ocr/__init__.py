#!/usr/bin/env python3
from __future__ import annotations

import os.path
from abc import abstractmethod, ABC
from typing import Union
from io import BytesIO
from pandas import DataFrame
from soup_files import File, Directory
from convert_stream import (
    ImageObject, DocumentPdf, PageDocumentPdf, MapText, ColumnsTable,
    get_hash_from_bytes, DEFAULT_LIB_IMAGE, LibImage
)
from ocr_stream.modules import (
    LibOcr, ModuleOcr, DEFAULT_LIB_OCR, MOD_PYOCR, MOD_PYTESSERACT,
    pytesseract, Output, pyocr,
)
from ocr_stream.bin_tess import BinTesseract

try:
    import pyocr.tesseract
except:
    pyocr = None


class TextRecognized(object):
    """
        Recebe os bytes de uma página PDF reconhecida de imagem
    e exporta para vários tipos de dados.
    """

    def __init__(self, bytes_recognized: bytes):
        self.bytes_recognized: bytes = bytes_recognized
        self.list_bad_char: list[str] = [
            ':', ',', ';', '$', '=',
            '!', '}', '{', '(', ')',
            '|', '\\', '‘', '*'
            '¢', '“', '\'', '¢', '"',
            '#', '.', '<', '?', '>',
            '»', '@', '+', '[', ']',
            '%', '~', '¥', '♀',
        ]

    def to_string(self) -> str | None:
        return self.to_page_pdf().to_string()

    def to_page_pdf(self) -> PageDocumentPdf:
        doc = self.to_document()
        return doc.to_pages()[0]

    def to_document(self) -> DocumentPdf:
        return DocumentPdf.create_from_bytes(BytesIO(self.bytes_recognized))

    def to_map(self, separator: str = '\n') -> MapText:
        text = self.to_string()
        if (text is None) or (text == '') or (text == 'nas'):
            return MapText([])
        try:
            return MapText(text.split(separator))
        except Exception as err:
            print(err)
            return MapText([])

    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        return self.to_map(separator).map_elements

    def to_dataframe(self, separator='\n') -> DataFrame:
        return self.to_map(separator).to_data()


class ABCOcrTesseract(ABC):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        if not bin_tess.exists():
            raise FileNotFoundError('tesseract binary not found')
        self.bin_tess: BinTesseract = bin_tess
        self.lang: str = lang
        self.tess_data_dir: str = tess_data_dir
        self.current_library: LibOcr = DEFAULT_LIB_OCR

    @abstractmethod
    def to_string(self, img: Union[File, ImageObject]) -> str:
        pass

    @abstractmethod
    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        pass


class IPytesseract(ABCOcrTesseract):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        super().__init__(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        self.current_library: LibOcr = LibOcr.PYTESSERACT
        self._MOD_TESS: pytesseract = pytesseract
        self._MOD_TESS.tesseract_cmd = self.bin_tess.get_tesseract().absolute()

    def __get_tess_dir_config(self) -> str | None:
        """
        https://github.com/h/pytesseract

        Example config: r'--tessdata-dir "C:\Program Files (x86)\Tesseract-OCR\tessdata"'
        tessdata_dir_config = r'--tessdata-dir <replace_with_your_tessdata_dir_path>'
        It's important to add double quotes around the dir path.
        """
        # Caminho para os dados de idioma, por, eng etc...
        # os.environ["TESSDATA_PREFIX"] = self.tess_data_dir.absolute()
        if self.tess_data_dir is None:
            return ''
        if not os.path.exists(self.tess_data_dir):
            return ''
        return r'--tessdata-dir "{}"'.format(self.tess_data_dir)

    def to_string(self, img: Union[File, ImageObject]) -> str:
        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()
        else:
            raise NotImplementedError()

        if self.lang is None:
            return self._MOD_TESS.image_to_string(_im, config=self.__get_tess_dir_config())
        else:
            return self._MOD_TESS.image_to_string(_im, lang=self.lang, config=self.__get_tess_dir_config())

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:

        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()
        else:
            raise NotImplementedError()
        bt = self._MOD_TESS.image_to_pdf_or_hocr(
            _im,
            lang=self.lang,
            config=self.__get_tess_dir_config()
        )
        return TextRecognized(bt)


# ======================================================================#
# Modulo OCR pyocr
# ======================================================================#

class IPyOcr(ABCOcrTesseract):

    def __init__(self, bin_tess: BinTesseract, *, lang: str = None, tess_data_dir: str = None):
        super().__init__(bin_tess, lang=lang, tess_data_dir=tess_data_dir)

        self.current_library: LibOcr = LibOcr.PYOCR
        pyocr_modules: list = pyocr.get_available_tools()
        if len(pyocr_modules) == 0:
            raise ValueError(f"{__class__.__name__} No OCR tool found")
        # The tools are returned in the recommended order of usage
        self._pyOcr = pyocr_modules[0]
        langs: list[str] = self._pyOcr.get_available_languages()
        if lang in langs:
            self.lang = lang
        else:
            self.lang = langs[0]

        # Ex: Will use tool 'libtesseract'
        print(f"Will use tool {self._pyOcr.get_name()}")

    def to_string(self, img: Union[File, ImageObject]) -> str:
        if isinstance(img, File):
            img = ImageObject.create_from_file(img)

        if DEFAULT_LIB_IMAGE == LibImage.OPENCV:
            _im = img.to_opencv()
        elif DEFAULT_LIB_IMAGE == LibImage.PIL:
            _im = img.to_pil()

        return self._pyOcr.to_string(
            _im,
            lang=self.lang,
            builder=pyocr.builders.TextBuilder()
        )

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        raise NotImplementedError(f'{__class__.__name__} método não implementado')


class TesseractOcr(object):

    def __init__(self, mod_ocr: ABCOcrTesseract):
        self.mod_ocr: ABCOcrTesseract = mod_ocr

    def to_string(self, img: Union[File, ImageObject]) -> str:
        return self.mod_ocr.to_string(img)

    def to_reconize(self, img: Union[File, ImageObject]) -> TextRecognized:
        return self.mod_ocr.to_reconize(img)

    @classmethod
    def create(
                cls,
                bin_tess: BinTesseract, *,
                lang: str = None,
                tess_data_dir: str = None,
                lib_ocr: LibOcr = DEFAULT_LIB_OCR,
            ) -> TesseractOcr:
        if lib_ocr == LibOcr.PYTESSERACT:
            md = IPytesseract(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        elif lib_ocr == LibOcr.PYOCR:
            md = IPyOcr(bin_tess, lang=lang, tess_data_dir=tess_data_dir)
        else:
            raise ValueError(f'{lib_ocr} is not supported')
        return cls(md)
