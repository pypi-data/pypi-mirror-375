# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrStats(shell.Task["MrStats.Outputs"]):
    """
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

    executable = "mrstats"

    # Arguments
    image_: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image from which statistics will be computed.""",
    )

    # Options

    # Statistics options:
    output: MultiInputObj[str] | None = shell.arg(
        default=None,
        argstr="-output",
        help="""output only the field specified. Multiple such options can be supplied if required. Choices are: mean, median, std, std_rv, min, max, count. Useful for use in scripts.  Both std options refer to the unbiased (sample) standard deviation. For complex data, min, max and std are calculated separately for real and imaginary parts, std_rv is based on the real valued variance (equals sqrt of sum of variances of imaginary and real parts).""",
        allowed_values=["mean", "median", "std", "std_rv", "min", "max", "count"],
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary mask image.""",
    )
    ignorezero: bool = shell.arg(
        default=False,
        argstr="-ignorezero",
        help="""ignore zero values during statistics calculation""",
    )

    # Additional options for mrstats:
    allvolumes: bool = shell.arg(
        default=False,
        argstr="-allvolumes",
        help="""generate statistics across all image volumes, rather than one set of statistics per image volume""",
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
