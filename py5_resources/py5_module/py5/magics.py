from IPython.display import display, SVG, Image
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring

import py5_tools


_unspecified = object()


@magics_class
class Py5Magics(Magics):

    @magic_arguments()
    @argument('width', type=int, help='width of SVG drawing')
    @argument('height', type=int, help='height of SVG drawing')
    @argument('--no-warnings', dest='suppress_warnings', action='store_true',
              help="suppress name conflict warnings")
    @cell_magic
    def py5drawsvg(self, line, cell):
        """Create an SVG image with py5 and embed result in the notebook.

        For users who are familiar with Processing and py5 programming, you can
        pretend the code in this cell will be executed in a sketch with no
        `draw()` function and your code in the `setup()` function. It will use
        the SVG renderer.

        The below example will create a red square on a gray background:

        %%py5drawsvg 500 250
        background(128)
        fill(255, 0, 0)
        rect(80, 100, 50, 50)

        As this is creating an SVG image, you cannot do operations on the
        `pixels` or `np_pixels` arrays. Use `%%py5draw` instead.

        Code used in this cell can reference functions and variables defined in
        other cells. This will create a name conflict if your functions and
        variables overlap with py5's. The name conflict may cause an error. If
        such a conflict is detected, py5 will issue a helpful warning to alert
        you to the potential problem. You can suppress warnings with the
        --no_warnings flag.
        """
        args = parse_argstring(self.py5drawsvg, line)
        svg = py5_tools.run_single_frame_sketch(
            'SVG', cell, args.width, args.height, user_ns=self.shell.user_ns,
            suppress_warnings=args.suppress_warnings)
        if svg:
            display(SVG(svg))

    @magic_arguments()
    @argument('width', type=int, help='width of PNG drawing')
    @argument('height', type=int, help='height of PNG drawing')
    @argument('--no-warnings', dest='suppress_warnings', action='store_true',
              help="suppress name conflict warnings")
    @cell_magic
    def py5draw(self, line, cell):
        """Create a PNG image with py5 and embed result in the notebook.

        For users who are familiar with Processing and py5 programming, you can
        pretend the code in this cell will be executed in a sketch with no
        `draw()` function and your code in the `setup()` function. It will use
        the default renderer.

        The below example will create a red square on a gray background:

        %%py5draw 500 250
        background(128)
        fill(255, 0, 0)
        rect(80, 100, 50, 50)

        Code used in this cell can reference functions and variables defined in
        other cells. This will create a name conflict if your functions and
        variables overlap with py5's. The name conflict may cause an error. If
        such a conflict is detected, py5 will issue a helpful warning to alert
        you to the potential problem. You can suppress warnings with the
        --no_warnings flag.
        """
        args = parse_argstring(self.py5draw, line)
        png = py5_tools.run_single_frame_sketch(
            'HIDDEN', cell, args.width, args.height, user_ns=self.shell.user_ns,
            suppress_warnings=args.suppress_warnings)
        if png:
            display(Image(png))


def load_ipython_extension(ipython):
    ipython.register_magics(Py5Magics)
