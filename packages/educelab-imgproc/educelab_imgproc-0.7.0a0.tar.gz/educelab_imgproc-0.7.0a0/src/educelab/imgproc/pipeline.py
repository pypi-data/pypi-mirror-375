from __future__ import annotations

import argparse
import textwrap
from functools import partial
from typing import Callable, List, Tuple, Dict

from educelab.cmdparse import parse, parse_parameter_list
from numpy.typing import ArrayLike

from .adjust import brightness_contrast, exposure, shadows, shadows_highlights
from .correction import gamma_correction, normalize
from .enhance import clahe, clip, curves, stretch, stretch_percentile
from .filters import sharpen

CommandStrList = List[str]
Command = Tuple[str, Dict]
CommandList = List[Command]
Pipeline = Callable[[ArrayLike], ArrayLike]

_fn_map = {
    'brightness-contrast': brightness_contrast,
    'clahe': clahe,
    'clip': clip,
    'curves': curves,
    'exposure': exposure,
    'gamma': gamma_correction,
    'normalize': normalize,
    'shadows': shadows,
    'shadows-highlights': shadows_highlights,
    'sharpen': sharpen,
    'stretch': stretch,
    'pstretch': stretch_percentile
}


def commands_description() -> str:
    return textwrap.dedent("""\
    -brightness-contrast=BRIGHTNESS{,CONTRAST}
    \t\t\tBrightness/contrast adjustment
    -clahe{=KERNEL{,BINS}}
    \t\t\tContrast Limited Adaptive Histogram Equalization
    -clip{=MIN{,MAX}}
    \t\t\tClip values to range
    -curves{=X0,Y0:X1,Y1:...:Xn,Yn}
    \t\t\tCurves enhancement. Provide a series of semicolon separated XY pairs.
    -exposure{=VAL}
    \t\t\tAdjust image exposure
    -gamma{=GAMMA{,GAIN}}
    \t\t\tGamma correction
    -normalize
    \t\t\tLinear contrast stretch to data min/max
    -shadows=VAL
    \t\t\tAdjust shadow brightness
    -shadows-highlights=SHADOWS,HIGHLIGHTS{,COMPRESS}
    \t\t\tAdjust shadows and highlights
    -sharpen{=RADIUS{,AMOUNT}}
    \t\t\tUnsharp masking filter
    -stretch=MIN,MAX
    \t\t\tLinear contrast stretch to absolute values
    -pstretch=MIN,MAX
    \t\t\tLinear contrast stretch to data percentiles
    """)


class Parsers:
    """cmdparse namespace for parsing enhancement command arguments."""

    @staticmethod
    def brightness_contrast(sep, val):
        defaults = {'b': 0., 'c': 0.}
        parsed = parse_parameter_list(val, ['b', 'c'], [float, float],
                                      num_required=1, mode='+')
        return defaults | parsed

    @staticmethod
    def clahe(sep, val):
        defaults = {'kernel_size': None, 'nbins': 256}
        parsed = parse_parameter_list(val, ['kernel_size', 'nbins'], [int, int])
        return defaults | parsed

    @staticmethod
    def clip(sep, val):
        defaults = {'a_min': 0., 'a_max': 1.}
        parsed = parse_parameter_list(val, ['a_min', 'a_max'], [float, float])
        return defaults | parsed

    @staticmethod
    def curves(sep, val):
        if val == '':
            return {'x': [[0., 0.], [0.207, 0.118], [0.513, 0.473], [1., 1.]]}

        node_list = val.split(':')
        node_list = [n.split(',') for n in node_list]
        for idx, n in enumerate(node_list):
            if len(n) != 2:
                raise ValueError(f'Unsupported curves parameter: {",".join(n)}')
        node_list = [[float(n[0]), float(n[1])] for n in node_list]

        return {'x': node_list}

    @staticmethod
    def exposure(sep, val):
        defaults = {'val': 1.}
        parsed = parse_parameter_list(val, ['val'], [float])
        return defaults | parsed

    @staticmethod
    def gamma(sep, val):
        defaults = {'gamma': 1., 'gain': 1.}
        parsed = parse_parameter_list(val, ['gamma', 'gain'],
                                      [float, float])
        return defaults | parsed

    @staticmethod
    def normalize(sep, val):
        if sep != '' or val != '':
            raise ValueError('-normalize does not take parameters')
        return {}

    @staticmethod
    def shadows(sep, val):
        return parse_parameter_list(val, ['val'], [float], num_required=1,
                                    mode='+')

    @staticmethod
    def shadows_highlights(sep, val):
        return parse_parameter_list(val, ['shadows_gain', 'highlights_gain',
                                          'compress'], [float, float, float],
                                    num_required=2, mode='+')

    @staticmethod
    def sharpen(sep, val):
        defaults = {'radius': 1., 'amount': 1.}
        parsed = parse_parameter_list(val, ['radius', 'amount'], [float, float])
        return defaults | parsed

    @staticmethod
    def stretch(sep, val):
        return parse_parameter_list(val, ['a_min', 'a_max'], [float, float],
                                    num_required=2, mode='+')

    @staticmethod
    def pstretch(sep, val):
        return parse_parameter_list(val, ['min_perc', 'max_perc'],
                                    [float, float], num_required=2, mode='+')


def build_pipeline(cmd_list: CommandList) -> Pipeline:
    """Convert parsed commands into an enhancement pipeline function.

    :param cmd_list: Parsed command list.
    :return: Pipeline callable function.
    """
    pipeline = []
    for (cmd, kwargs) in cmd_list:
        fn = partial(_fn_map[cmd], **kwargs)
        pipeline.append(fn)

    def pipeline_fn(img):
        for p in pipeline:
            img = p(img)
        return img

    return pipeline_fn


def parse_and_build(cmd_strs: CommandStrList) -> Tuple[Pipeline, CommandList]:
    """Parse command arguments and build the pipeline function.

    :param cmd_strs: List of commands returned by argparse.
    :return: Pipeline callable function, parsed command list.
    """
    cmds = parse(cmd_strs, Parsers)
    apply_fn = build_pipeline(cmds)
    return apply_fn, cmds


def add_parser_enhancement_group(parser):
    """Adds the enhancement commands group and positional arguments to the
    given parser."""
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    opts = parser.add_argument_group('enhancement commands')
    opts.add_argument('commands', metavar='CMD', nargs='*')
    opts.description = commands_description()
    return opts
