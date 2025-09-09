# -*- coding: utf-8 -*-
import importlib
from typing import Callable

from sinapsis.templates import _import_template_package

_root_lib_path = "sinapsis_easyocr.templates"

_template_lookup = {
    "EasyOCR": f"{_root_lib_path}.easy_ocr",
}

_ADDITIONAL_TEMPLATE_MODULES: list = []
for t_module in _ADDITIONAL_TEMPLATE_MODULES:
    _template_lookup |= _import_template_package(t_module)


def __getattr__(name: str) -> Callable:
    if name in _template_lookup:
        module = importlib.import_module(_template_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"template `{name}` not found in {_root_lib_path}")


__all__ = list(_template_lookup.keys())
