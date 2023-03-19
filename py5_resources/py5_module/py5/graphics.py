# *****************************************************************************
#
#   Part of the py5 library
#   Copyright (C) 2020-2023 Jim Schmitz
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
from typing import overload  # noqa
import weakref
import types

import numpy as np  # noqa
import numpy.typing as npt  # noqa

from jpype import JClass

from .base import Py5Base
from .mixins import PixelPy5GraphicsMixin
from .font import Py5Font  # noqa
from .shader import Py5Shader, _return_py5shader, _load_py5shader  # noqa
from .shape import Py5Shape, _return_py5shape, _load_py5shape  # noqa
from .image import Py5Image, _return_py5image  # noqa
from .decorators import _text_fix_str, _convert_hex_color, _context_wrapper  # noqa
from .pmath import _get_matrix_wrapper  # noqa
from . import spelling


py5graphics_class_members_code = None  # DELETE


def _return_py5graphics(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        ret = f(self_, *args)
        if ret is not None:
            return Py5Graphics(ret)
    return decorated


def _name_renderer(renderer_name, clsname):
    def _decorator(f):
        @functools.wraps(f)
        def decorated(self_, *args):
            return f(self_, *args, _renderer_name=renderer_name, _clsname=clsname)
        return decorated
    return _decorator


_Py5GraphicsHelper = JClass('py5.core.Py5GraphicsHelper')


class Py5Graphics(PixelPy5GraphicsMixin, Py5Base):
    """$classdoc_Py5Graphics
    """
    _py5_object_cache = weakref.WeakSet()

    PI = np.pi
    HALF_PI = np.pi / 2
    THIRD_PI = np.pi / 3
    QUARTER_PI = np.pi / 4
    TWO_PI = 2 * np.pi
    TAU = 2 * np.pi
    RAD_TO_DEG = 180 / np.pi
    DEG_TO_RAD = np.pi / 180

    def __new__(cls, pgraphics):
        for o in cls._py5_object_cache:
            if pgraphics == o._instance:
                return o
        else:
            o = object.__new__(Py5Graphics)
            cls._py5_object_cache.add(o)
            return o

    def __init__(self, pgraphics):
        if pgraphics == getattr(self, '_instance', None):
            # this is a cached Py5Graphics object, don't re-run __init__()
            return

        self._instance = pgraphics
        super().__init__(instance=pgraphics)
        self._dictionary = set(dir(self))

    def __str__(self) -> str:
        return f"Py5Graphics(width=" + str(self._get_width()) + ", height=" + str(self._get_height()) + ")"

    def __repr__(self) -> str:
        return self.__str__()

    def __getattr__(self, name):
        msg = 'Py5Graphics objects have no fields or methods named "' + name + '"'
        if (suggestions := spelling.suggestions(name, self._dictionary)):
            msg += '. Did you mean ' + suggestions + '?'
        raise AttributeError(msg)

    def _activate_context_manager(self, exit_function, exit_args):
        self._context_manager_exit_function = exit_function
        self._context_manager_exit_args = exit_args

    def __enter__(self):
        if not (hasattr(self, '_context_manager_exit_function') and hasattr(self, '_context_manager_exit_args')):
            raise RuntimeError('Cannot use this Py5Graphics object as a context manager')
        return self

    def __exit__(self, *exc):
        self._context_manager_exit_function(*self._context_manager_exit_args)

    def points(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.points(self._instance, coordinates)

    def lines(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.lines(self._instance, coordinates)

    def vertices(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.vertices(self._instance, coordinates)

    def bezier_vertices(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.bezierVertices(self._instance, coordinates)

    def curve_vertices(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.curveVertices(self._instance, coordinates)

    def quadratic_vertices(self, coordinates):
        if isinstance(coordinates, types.GeneratorType):
            coordinates = list(coordinates)
        _Py5GraphicsHelper.quadraticVertices(self._instance, coordinates)


{py5graphics_class_members_code}
