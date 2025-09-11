# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrMetric(shell.Task["MrMetric.Outputs"]):
    """Currently only the mean squared difference is fully implemented.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au) and Max Pietsch (maximilian.pietsch@kcl.ac.uk)

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

    executable = "mrmetric"

    # Arguments
    image1: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the first input image.""",
    )
    image2: ImageIn = shell.arg(
        argstr="",
        position=2,
        help="""the second input image.""",
    )

    # Options
    space: str | None = shell.arg(
        default=None,
        argstr="-space",
        help="""Image "space" in which the metric will be computed. Options are: voxel: per voxel; image1: scanner space of image 1; image2: scanner space of image 2; average: scanner space of the average affine transformation of image 1 and 2; default: voxel.""",
        allowed_values=["voxel", "image1", "image2", "average"],
    )
    interp: str | None = shell.arg(
        default=None,
        argstr="-interp",
        help="""set the interpolation method to use when reslicing (choices: nearest, linear, cubic, sinc. Default: linear).""",
        allowed_values=["nearest", "linear", "cubic", "sinc"],
    )
    metric: str | None = shell.arg(
        default=None,
        argstr="-metric",
        help="""define the dissimilarity metric used to calculate the cost. Choices: diff (squared differences); cc (non-normalised negative cross correlation aka negative cross covariance). Default: diff). cc is only implemented for -space average and -interp linear and cubic.""",
        allowed_values=["diff", "cc"],
    )
    mask1: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask1",
        help="""mask for image 1""",
    )
    mask2: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask2",
        help="""mask for image 2""",
    )
    nonormalisation: bool = shell.arg(
        default=False,
        argstr="-nonormalisation",
        help="""do not normalise the dissimilarity metric to the number of voxels.""",
    )
    overlap: bool = shell.arg(
        default=False,
        argstr="-overlap",
        help="""output number of voxels that were used.""",
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
        pass
