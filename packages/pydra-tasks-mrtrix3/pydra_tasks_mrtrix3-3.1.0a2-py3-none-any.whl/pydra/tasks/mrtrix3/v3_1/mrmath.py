# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrMath(shell.Task["MrMath.Outputs"]):
    """Supported operations are:

        mean, median, sum, product, rms (root-mean-square value), norm (vector 2-norm), var (unbiased variance), std (unbiased standard deviation), min, max, absmax (maximum absolute value), magmax (value with maximum absolute value, preserving its sign).

        This command is used to traverse either along an image axis, or across a set of input images, calculating some statistic from the values along each traversal. If you are seeking to instead perform mathematical calculations that are done independently for each voxel, pleaase see the 'mrcalc' command.


        Example usages
        --------------


        Calculate a 3D volume representing the mean intensity across a 4D image series:

        `$ mrmath 4D.mif mean 3D_mean.mif -axis 3`

        This is a common operation for calculating e.g. the mean value within a specific DWI b-value. Note that axis indices start from 0; thus, axes 0, 1 & 2 are the three spatial axes, and axis 3 operates across volumes.


        Generate a Maximum Intensity Projection (MIP) along the inferior-superior direction:

        `$ mrmath input.mif max MIP.mif -axis 2`

        Since a MIP is literally the maximal value along a specific projection direction, axis-aligned MIPs can be generated easily using mrmath with the 'max' operation.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: J-Donald Tournier (jdtournier@gmail.com)

        Copyright: Copyright (c) 2008-2025 the MRtrix3 contributors.

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Covered Software is provided under this License on an "as is"
    basis, without warranty of any kind, either expressed, implied, or
    statutory, including, without limitation, warranties that the
    Covered Software is free of defects, merchantable, fit for a
    particular purpose or non-infringing.
    See the Mozilla Public License v. 2.0 for more details.

    For more details, see http://www.mrtrix.org/.
    """

    executable = "mrmath"

    # Arguments
    in_file: MultiInputObj[ImageIn] = shell.arg(
        argstr="",
        position=1,
        help="""the input image(s).""",
    )
    operation: str = shell.arg(
        argstr="",
        position=2,
        help="""the operation to apply; one of: mean, median, sum, product, rms, norm, var, std, min, max, absmax, magmax.""",
        allowed_values=[
            "mean",
            "median",
            "sum",
            "product",
            "rms",
            "norm",
            "var",
            "std",
            "min",
            "max",
            "absmax",
            "magmax",
        ],
    )

    # Options
    axis: int | None = shell.arg(
        default=None,
        argstr="-axis",
        help="""perform operation along a specified axis of a single input image""",
    )
    keep_unary_axes: bool = shell.arg(
        default=False,
        argstr="-keep_unary_axes",
        help="""Keep unary axes in input images prior to calculating the stats. The default is to wipe axes with single elements.""",
    )

    # Data type options:
    datatype: str | None = shell.arg(
        default=None,
        argstr="-datatype",
        help="""specify output image data type. Valid choices are: float16, float16le, float16be, float32, float32le, float32be, float64, float64le, float64be, int64, uint64, int64le, uint64le, int64be, uint64be, int32, uint32, int32le, uint32le, int32be, uint32be, int16, uint16, int16le, uint16le, int16be, uint16be, cfloat16, cfloat16le, cfloat16be, cfloat32, cfloat32le, cfloat32be, cfloat64, cfloat64le, cfloat64be, int8, uint8, bit.""",
        allowed_values=[
            "float16",
            "float16le",
            "float16be",
            "float32",
            "float32le",
            "float32be",
            "float64",
            "float64le",
            "float64be",
            "int64",
            "uint64",
            "int64le",
            "uint64le",
            "int64be",
            "uint64be",
            "int32",
            "uint32",
            "int32le",
            "uint32le",
            "int32be",
            "uint32be",
            "int16",
            "uint16",
            "int16le",
            "uint16le",
            "int16be",
            "uint16be",
            "cfloat16",
            "cfloat16le",
            "cfloat16be",
            "cfloat32",
            "cfloat32le",
            "cfloat32be",
            "cfloat64",
            "cfloat64le",
            "cfloat64be",
            "int8",
            "uint8",
            "bit",
        ],
    )

    # Standard options
    info: bool = shell.arg(
        default=False,
        argstr="-info",
        help="""display information messages.""",
    )
    quiet: bool = shell.arg(
        default=False,
        argstr="-quiet",
        help="""do not display information messages or progress status; alternatively, this can be achieved by setting the MRTRIX_QUIET environment variable to a non-empty string.""",
    )
    debug: bool = shell.arg(
        default=False,
        argstr="-debug",
        help="""display debugging messages.""",
    )
    force: bool = shell.arg(
        default=False,
        argstr="-force",
        help="""force overwrite of output files (caution: using the same file as input and output might cause unexpected behaviour).""",
    )
    nthreads: int | None = shell.arg(
        default=None,
        argstr="-nthreads",
        help="""use this number of threads in multi-threaded applications (set to 0 to disable multi-threading).""",
    )
    config: MultiInputObj[tuple[str, str]] | None = shell.arg(
        default=None,
        argstr="-config",
        help="""temporarily set the value of an MRtrix config file entry.""",
        sep=" ",
    )

    class Outputs(shell.Outputs):
        out_file: ImageOut = shell.outarg(
            argstr="",
            position=3,
            path_template="out_file.mif",
            help="""the output image.""",
        )
