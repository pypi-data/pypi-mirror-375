# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Warp2Metric(shell.Task["Warp2Metric.Outputs"]):
    """Fixel data are stored utilising the fixel directory format described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/fixel_based_analysis/fixel_directory_format.html


        References
        ----------

            Raffelt, D.; Tournier, JD/; Smith, RE.; Vaughan, DN.; Jackson, G.; Ridgway, GR. Connelly, A. Investigating White Matter Fibre Density and Morphology using Fixel-Based Analysis. Neuroimage, 2017, 144, 58-73. doi: 10.1016/j.neuroimage.2016.09.029

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

    executable = "warp2metric"

    # Arguments
    in_: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input deformation field""",
    )

    # Options
    fc: tuple[ImageIn, ImageIn, ImageIn] | None = shell.arg(
        default=None,
        argstr="-fc",
        help="""use an input template fixel image to define fibre orientations and output a fixel image describing the change in fibre cross-section (FC) in the perpendicular plane to the fixel orientation.""",
        sep=" ",
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
        jmat: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-jmat",
            path_template="jmat.mif",
            help="""output a Jacobian matrix image stored in column-major order along the 4th dimension. Note the output jacobian describes the warp gradient w.r.t the scanner space coordinate system""",
        )
        jdet: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-jdet",
            path_template="jdet.mif",
            help="""output the Jacobian determinant instead of the full matrix""",
        )
