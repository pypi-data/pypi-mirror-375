# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckSample(shell.Task["TckSample.Outputs"]):
    """By default, the value of the underlying image at each point along the track is written to either an ASCII file (with all values for each track on the same line), or a track scalar file (.tsf). Alternatively, some statistic can be taken from the values along each streamline and written to a vector file.


        References
        ----------

            * If using -precise option: Smith, R. E.; Tournier, J.-D.; Calamante, F. & Connelly, A. SIFT: Spherical-deconvolution informed filtering of tractograms. NeuroImage, 2013, 67, 298-312

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

    executable = "tcksample"

    # Arguments
    tracks: Tracks = shell.arg(
        argstr="",
        position=1,
        help="""the input track file""",
    )
    image_: ImageIn = shell.arg(
        argstr="",
        position=2,
        help="""the image to be sampled""",
    )

    # Options
    stat_tck: str | None = shell.arg(
        default=None,
        argstr="-stat_tck",
        help="""compute some statistic from the values along each streamline; (options are: mean,median,min,max)""",
        allowed_values=["mean", "median", "min", "max"],
    )
    nointerp: bool = shell.arg(
        default=False,
        argstr="-nointerp",
        help="""do not use trilinear interpolation when sampling image values""",
    )
    precise: bool = shell.arg(
        default=False,
        argstr="-precise",
        help="""use the precise mechanism for mapping streamlines to voxels (obviates the need for trilinear interpolation)  (only applicable if some per-streamline statistic is requested)""",
    )
    use_tdi_fraction: bool = shell.arg(
        default=False,
        argstr="-use_tdi_fraction",
        help="""each streamline is assigned a fraction of the image intensity in each voxel based on the fraction of the track density contributed by that streamline (this is only appropriate for processing a whole-brain tractogram, and images for which the quantiative parameter is additive)""",
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
        values: File = shell.outarg(
            argstr="",
            position=3,
            path_template="values.txt",
            help="""the output sampled values""",
        )
