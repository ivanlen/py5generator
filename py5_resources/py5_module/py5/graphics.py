# *****************************************************************************
#
#   Part of the py5 library
#   Copyright (C) 2020-2021 Jim Schmitz
#
#   This library is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 2.1 of the License, or (at
#   your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
#   General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this library. If not, see <https://www.gnu.org/licenses/>.
#
# *****************************************************************************
# *** FORMAT PARAMS ***
from __future__ import annotations

import functools
from typing import overload, List  # noqa
from nptyping import NDArray, Float  # noqa

import numpy as np  # noqa

from jpype import JClass

from .base import Py5Base
from .mixins import PixelMixin
from .font import Py5Font  # noqa
from .shader import Py5Shader, _return_py5shader, _load_py5shader  # noqa
from .shape import Py5Shape, _return_py5shape, _load_py5shape  # noqa
from .image import Py5Image, _return_py5image  # noqa
from .type_decorators import _text_fix_str  # noqa
from .pmath import _get_matrix_wrapper  # noqa
from . import image_conversion


py5graphics_class_members_code = None  # DELETE


def py5graphics_precondition(obj):
    return isinstance(obj, Py5Graphics)


def py5graphics_converter(py5graphics):
    return py5graphics._instance


image_conversion.register_image_conversion(
    py5graphics_precondition, py5graphics_converter)


def _return_py5graphics(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        ret = f(self_, *args)
        if ret is not None:
            return Py5Graphics(ret)
    return decorated


_Py5GraphicsHelper = JClass('py5.core.Py5GraphicsHelper')


class Py5Graphics(PixelMixin, Py5Base):
    """$classdoc_Py5Graphics
    """

    def __init__(self, pgraphics):
        self._instance = pgraphics
        super().__init__(instance=pgraphics)

    def points(self, coordinates):
        _Py5GraphicsHelper.points(self._instance, coordinates)

    def lines(self, coordinates):
        _Py5GraphicsHelper.lines(self._instance, coordinates)

    def vertices(self, coordinates):
        _Py5GraphicsHelper.vertices(self._instance, coordinates)

    def bezier_vertices(self, coordinates):
        _Py5GraphicsHelper.bezierVertices(self._instance, coordinates)

    def curve_vertices(self, coordinates):
        _Py5GraphicsHelper.curveVertices(self._instance, coordinates)

    def quadratic_vertices(self, coordinates):
        _Py5GraphicsHelper.quadraticVertices(self._instance, coordinates)


{py5graphics_class_members_code}
