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
import re
import io
from pathlib import Path
import tempfile
import textwrap

from IPython.display import display, SVG, Image
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.magic_arguments import parse_argstring, argument, magic_arguments, kwds

import PIL

from .util import fix_triple_quote_str, CellMagicHelpFormatter, ZMQHelper
from .. import imported


_CODE_FRAMEWORK = """
import py5

with open('{0}', 'r') as f:
    eval(compile(f.read(), '{0}', 'exec'))

py5.run_sketch(block=True, sketch_functions=dict(settings=_py5_settings, setup=_py5_setup))
if py5.is_dead_from_error:
    py5.exit_sketch()
"""


_CODE_FRAMEWORK_IMPORTED_MODE = """
with open('{0}', 'r') as f:
    eval(compile(f.read(), '{0}', 'exec'))

run_sketch(block=True, sketch_functions=dict(settings=_py5_settings, setup=_py5_setup))
if is_dead_from_error:
    exit_sketch()
"""


_STANDARD_CODE_TEMPLATE = """
def _py5_settings():
    py5.size({0}, {1}, py5.{2})


def _py5_setup():
{4}

    py5.get(0, 0, {0}, {1}).save("{3}", use_thread=False)
    py5.exit_sketch()
"""


_SAVE_OUTPUT_CODE_TEMPLATE = """
def _py5_settings():
    py5.size({0}, {1}, py5.{2}, "{3}")


def _py5_setup():
{4}

    py5.exit_sketch()
"""


_DXF_CODE_TEMPLATE = """
def _py5_settings():
    py5.size({0}, {1}, py5.P3D)


def _py5_setup():
    py5.begin_raw(py5.DXF, "{3}")

{4}

    py5.end_raw()
    py5.exit_sketch()
"""


def _run_sketch(renderer, zmq_streamer, code, width, height, user_ns, safe_exec):
    if renderer == 'SVG':
        template = _SAVE_OUTPUT_CODE_TEMPLATE
        suffix = '.svg'
        read_mode = 'r'
    elif renderer == 'PDF':
        template = _SAVE_OUTPUT_CODE_TEMPLATE
        suffix = '.pdf'
        read_mode = 'rb'
    elif renderer == 'DXF':
        template = _DXF_CODE_TEMPLATE
        suffix = '.dxf'
        read_mode = 'r'
    else:
        template = _STANDARD_CODE_TEMPLATE
        suffix = '.png'
        read_mode = 'rb'

    import py5
    is_running = py5.is_running
    if (isinstance(is_running, bool) and is_running) or (callable(is_running) and is_running()) :
        zmq_streamer('stderr', 'You must exit the currently running sketch before running another sketch.')
        return None

    if imported.get_imported_mode():
        template = template.replace('py5.', '')
        code_framework = _CODE_FRAMEWORK_IMPORTED_MODE
    else:
        code_framework = _CODE_FRAMEWORK

    if safe_exec:
        prepared_code = textwrap.indent(code, '    ')
        prepared_code = fix_triple_quote_str(prepared_code)
    else:
        user_ns['_py5_user_ns'] = user_ns
        code = code.replace('"""', r'\"\"\"')
        prepared_code = f'    exec("""{code}""", _py5_user_ns)'

    with tempfile.TemporaryDirectory() as tempdir:
        temp_py = Path(tempdir) / 'py5_code.py'
        temp_out = Path(tempdir) / ('output' + suffix)

        with open(temp_py, 'w') as f:
            code = template.format(
                width, height, renderer, temp_out.as_posix(), prepared_code)
            f.write(code)

        exec(code_framework.format(temp_py.as_posix()), user_ns)

        if temp_out.exists():
            with open(temp_out, read_mode) as f:
                result = f.read()
        else:
            result = None

    if not safe_exec:
        del user_ns['_py5_user_ns']

    return result


@magics_class
class DrawingMagics(Magics, ZMQHelper):

    def _filename_check(self, filename):
        filename = Path(filename)
        if not filename.parent.exists():
            filename.parent.mkdir(parents=True)
        return filename

    def _variable_name_check(self, varname):
        return re.match('^[a-zA-Z_]\w*' + chr(36), varname)

    @magic_arguments()
    @argument(""" DELETE
    $arguments_Py5Magics_py5drawpdf_arguments
    """)  # DELETE
    @kwds(formatter_class=CellMagicHelpFormatter)
    @cell_magic
    def py5drawpdf(self, line, cell):
        """$class_Py5Magics_py5drawpdf"""
        args = parse_argstring(self.py5drawpdf, line)

        display_pub = self.shell.display_pub
        parent_header = display_pub.parent_header
        zmq_streamer = self._make_zmq_streamer(display_pub, parent_header)

        pdf = _run_sketch('PDF', zmq_streamer, cell, args.width, args.height,
                          self.shell.user_ns, not args.unsafe)
        if pdf:
            filename = self._filename_check(args.filename)
            with open(filename, 'wb') as f:
                f.write(pdf)
            zmq_streamer('stdout', f'PDF written to {filename}')

    @magic_arguments()
    @argument(""" DELETE
    $arguments_Py5Magics_py5drawdxf_arguments
    """)  # DELETE
    @kwds(formatter_class=CellMagicHelpFormatter)
    @cell_magic
    def py5drawdxf(self, line, cell):
        """$class_Py5Magics_py5drawdxf"""
        args = parse_argstring(self.py5drawdxf, line)

        display_pub = self.shell.display_pub
        parent_header = display_pub.parent_header
        zmq_streamer = self._make_zmq_streamer(display_pub, parent_header)

        dxf = _run_sketch('DXF', zmq_streamer, cell, args.width, args.height,
                          self.shell.user_ns, not args.unsafe)
        if dxf:
            filename = self._filename_check(args.filename)
            with open(filename, 'w') as f:
                f.write(dxf)
            zmq_streamer('stdout', f'DXF written to {filename}')

    @magic_arguments()
    @argument(""" DELETE
    $arguments_Py5Magics_py5drawsvg_arguments
    """)  # DELETE
    @kwds(formatter_class=CellMagicHelpFormatter)
    @cell_magic
    def py5drawsvg(self, line, cell):
        """$class_Py5Magics_py5drawsvg"""
        args = parse_argstring(self.py5drawsvg, line)

        display_pub = self.shell.display_pub
        parent_header = display_pub.parent_header
        zmq_streamer = self._make_zmq_streamer(display_pub, parent_header)

        svg = _run_sketch('SVG', zmq_streamer, cell, args.width, args.height,
                          self.shell.user_ns, not args.unsafe)
        if svg:
            if args.filename:
                filename = self._filename_check(args.filename)
                with open(filename, 'w') as f:
                    f.write(svg)
                zmq_streamer('stdout', f'SVG drawing written to {filename}')
            display(SVG(svg))

    @magic_arguments()
    @argument(""" DELETE
    $arguments_Py5Magics_py5draw_arguments
    """)  # DELETE
    @kwds(formatter_class=CellMagicHelpFormatter)
    @cell_magic
    def py5draw(self, line, cell):
        """$class_Py5Magics_py5draw"""
        args = parse_argstring(self.py5draw, line)

        display_pub = self.shell.display_pub
        parent_header = display_pub.parent_header
        zmq_streamer = self._make_zmq_streamer(display_pub, parent_header)

        if args.renderer == 'SVG':
            zmq_streamer('stderr', 'please use %%py5drawsvg for SVG drawings.')
            return
        if args.renderer == 'PDF':
            zmq_streamer('stderr', 'please use %%py5drawpdf for PDFs.')
            return
        if args.renderer not in ['HIDDEN', 'JAVA2D', 'P2D', 'P3D']:
            zmq_streamer('stderr', f'unknown renderer {args.renderer}')
            return

        png = _run_sketch(args.renderer, zmq_streamer, cell, args.width, args.height,
                          self.shell.user_ns, not args.unsafe)
        if png:
            if args.filename or args.variable:
                pil_img = PIL.Image.open(io.BytesIO(png)).convert(mode='RGB')
                if args.filename:
                    filename = self._filename_check(args.filename)
                    pil_img.save(filename)
                    zmq_streamer('stdout', f'PNG file written to {filename}')
                if args.variable:
                    if self._variable_name_check(args.variable):
                        self.shell.user_ns[args.variable] = pil_img
                        zmq_streamer('stdout', f'PIL Image assigned to {args.variable}')
                    else:
                        zmq_streamer('stderr', f'Invalid variable name {args.variable}')
            display(Image(png))
