#!/usr/bin/env python3
from __future__ import annotations
from enum import Enum
from typing import Union, TypeAlias


class LibOcr(Enum):

    PYTESSERACT = "pytesseract"
    PYOCR = "pyocr"
    NOT_IMPLEMENTED = "not_implemented"


MOD_PYTESSERACT: bool = False
MOD_PYOCR: bool = False

try:
    from pytesseract import pytesseract, Output
    MOD_PYTESSERACT = True
except:
    pytesseract = None
    Output = None

try:
    import pyocr
    import pyocr.tesseract
    MOD_PYOCR = True
except:
    pyocr = None
    pyocr.tesseract = None

if MOD_PYTESSERACT and MOD_PYOCR:
    ModuleOcr: TypeAlias = Union[pyocr, pytesseract]
    DEFAULT_LIB_OCR = LibOcr.PYTESSERACT
elif MOD_PYTESSERACT:
    ModuleOcr: TypeAlias = Union[pytesseract]
    DEFAULT_LIB_OCR = LibOcr.PYTESSERACT
elif MOD_PYOCR:
    ModuleOcr: TypeAlias = Union[pyocr]
    DEFAULT_LIB_OCR = LibOcr.PYOCR
else:
    ModuleOcr: TypeAlias = None
    DEFAULT_LIB_OCR = LibOcr.NOT_IMPLEMENTED
