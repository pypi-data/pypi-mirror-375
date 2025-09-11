# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class WarpConvert(shell.Task["WarpConvert.Outputs"]):
    """A deformation field is defined as an image where each voxel defines the corresponding position in the other image (in scanner space coordinates). A displacement field stores the displacements (in mm) to the other image from each voxel's position (in scanner space). The warpfull file is the 5D format output from mrregister -nl_warp_full, which contains linear transforms, warps and their inverses that map each image to a midway space.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au)

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

    executable = "warpconvert"

    # Arguments
    in_: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input warp image.""",
    )
    type: str = shell.arg(
        argstr="",
        position=2,
        help="""the conversion type required; valid choices are: deformation2displacement, displacement2deformation, warpfull2deformation, warpfull2displacement""",
        allowed_values=[
            "deformation2displacement",
            "displacement2deformation",
            "warpfull2deformation",
            "warpfull2displacement",
        ],
    )

    # Options
    template: ImageIn | None = shell.arg(
        default=None,
        argstr="-template",
        help="""define a template image when converting a warpfull file (which is defined on a grid in the midway space between image 1 & 2). For example, to generate the deformation field that maps image1 to image2, then supply image2 as the template image""",
    )
    midway_space: bool = shell.arg(
        default=False,
        argstr="-midway_space",
        help="""to be used only with warpfull2deformation and warpfull2displacement conversion types. The output will only contain the non-linear warp to map an input image to the midway space (defined by the warpfull grid). If a linear transform exists in the warpfull file header then it will be composed and included in the output.""",
    )
    from_: int | None = shell.arg(
        default=None,
        argstr="-from",
        help="""to be used only with warpfull2deformation and warpfull2displacement conversion types. Used to define the direction of the desired output field. Use -from 1 to obtain the image1->image2 field and from 2 for image2->image1. Can be used in combination with the -midway_space option  to produce a field that only maps to midway space.""",
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
        out: ImageOut = shell.outarg(
            argstr="",
            position=3,
            path_template="out.mif",
            help="""the output warp image.""",
        )
