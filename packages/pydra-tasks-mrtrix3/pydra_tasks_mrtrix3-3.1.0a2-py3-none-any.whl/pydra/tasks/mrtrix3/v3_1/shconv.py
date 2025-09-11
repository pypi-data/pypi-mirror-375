# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class ShConv(shell.Task["ShConv.Outputs"]):
    """Provided with matching pairs of response function and ODF images (containing SH coefficients), perform spherical convolution to provide the corresponding SH coefficients of the signal.

        If multiple pairs of inputs are provided, their contributions will be summed into a single output.

        If the responses are multi-shell (with one line of coefficients per shell), the output will be a 5-dimensional image, with the SH coefficients of the signal in each shell stored at different indices along the 5th dimension.

        The spherical harmonic coefficients are stored according to the conventions described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/concepts/spherical_harmonics.html

        The spherical harmonic coefficients are stored according to the conventions described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/concepts/spherical_harmonics.html


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au) and J-Donald Tournier (jdtournier@gmail.com)

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

    executable = "shconv"

    # Arguments
    odf_response: MultiInputObj[ty.Any] = shell.arg(
        argstr="",
        position=1,
        help="""pairs of input ODF image and corresponding responses""",
    )

    # Options

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

    # Stride options:
    strides: ty.Any = shell.arg(
        default=None,
        argstr="-strides",
        help="""specify the strides of the output data in memory; either as a comma-separated list of (signed) integers, or as a template image from which the strides shall be extracted and used. The actual strides produced will depend on whether the output image format can support it.""",
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
        SH_out: ImageOut = shell.outarg(
            argstr="",
            position=2,
            path_template="SH_out.mif",
            help="""the output spherical harmonics coefficients image.""",
        )
