# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrColour(shell.Task["MrColour.Outputs"]):
    """Under typical usage, this command will receive as input ad 3D greyscale image, and output a 4D image with 3 volumes corresponding to red-green-blue components; other use cases are possible, and are described in more detail below.

        By default, the command will automatically determine the maximum and minimum intensities of the input image, and use that information to set the upper and lower bounds of the applied colourmap. This behaviour can be overridden by manually specifying these bounds using the -upper and -lower options respectively.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Robert E. Smith (robert.smith@florey.edu.au)

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

    executable = "mrcolour"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image""",
    )
    map: str = shell.arg(
        argstr="",
        position=2,
        help="""the colourmap to apply; choices are: gray,hot,cool,jet,inferno,viridis,pet,colour,rgb""",
        allowed_values=[
            "gray",
            "hot",
            "cool",
            "jet",
            "inferno",
            "viridis",
            "pet",
            "colour",
            "rgb",
        ],
    )

    # Options
    upper: float | None = shell.arg(
        default=None,
        argstr="-upper",
        help="""manually set the upper intensity of the colour mapping""",
    )
    lower: float | None = shell.arg(
        default=None,
        argstr="-lower",
        help="""manually set the lower intensity of the colour mapping""",
    )
    colour: list[float] | None = shell.arg(
        default=None,
        argstr="-colour",
        help="""set the target colour for use of the 'colour' map (three comma-separated floating-point values)""",
        sep=",",
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
            help="""the output image""",
        )
