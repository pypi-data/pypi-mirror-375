# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckSift(shell.Task["TckSift.Outputs"]):
    """
        References
        ----------

            Smith, R. E.; Tournier, J.-D.; Calamante, F. & Connelly, A. SIFT: Spherical-deconvolution informed filtering of tractograms. NeuroImage, 2013, 67, 298-312

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

    executable = "tcksift"

    # Arguments
    in_tracks: Tracks = shell.arg(
        argstr="",
        position=1,
        help="""the input track file""",
    )
    in_fod: ImageIn = shell.arg(
        argstr="",
        position=2,
        help="""input image containing the spherical harmonics of the fibre orientation distributions""",
    )
    out_tracks: Tracks = shell.arg(
        argstr="",
        position=3,
        help="""the output filtered tracks file""",
    )

    # Options
    nofilter: bool = shell.arg(
        default=False,
        argstr="-nofilter",
        help="""do NOT perform track filtering; just construct the model in order to provide output debugging images""",
    )
    output_at_counts: list[int] | None = shell.arg(
        default=None,
        argstr="-output_at_counts",
        help="""output filtered track files (and optionally debugging images if -output_debug is specified) at specific numbers of remaining streamlines; provide as comma-separated list of integers""",
        sep=",",
    )

    # Options for setting the processing mask for the SIFT fixel-streamlines comparison model:
    proc_mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-proc_mask",
        help="""provide an image containing the processing mask weights for the model; image spatial dimensions must match the fixel image""",
    )
    act: ImageIn | None = shell.arg(
        default=None,
        argstr="-act",
        help="""use an ACT five-tissue-type segmented anatomical image to derive the processing mask""",
    )

    # Options affecting the SIFT model:
    fd_scale_gm: bool = shell.arg(
        default=False,
        argstr="-fd_scale_gm",
        help="""provide this option (in conjunction with -act) to heuristically downsize the fibre density estimates based on the presence of GM in the voxel. This can assist in reducing tissue interface effects when using a single-tissue deconvolution algorithm""",
    )
    no_dilate_lut: bool = shell.arg(
        default=False,
        argstr="-no_dilate_lut",
        help="""do NOT dilate FOD lobe lookup tables; only map streamlines to FOD lobes if the precise tangent lies within the angular spread of that lobe""",
    )
    make_null_lobes: bool = shell.arg(
        default=False,
        argstr="-make_null_lobes",
        help="""add an additional FOD lobe to each voxel, with zero integral, that covers all directions with zero / negative FOD amplitudes""",
    )
    remove_untracked: bool = shell.arg(
        default=False,
        argstr="-remove_untracked",
        help="""remove FOD lobes that do not have any streamline density attributed to them; this improves filtering slightly, at the expense of longer computation time (and you can no longer trivially do quantitative comparisons between reconstructions if this is enabled)""",
    )
    fd_thresh: float | None = shell.arg(
        default=None,
        argstr="-fd_thresh",
        help="""fibre density threshold; exclude an FOD lobe from filtering processing if its integral is less than this amount (streamlines will still be mapped to it, but it will not contribute to the cost function or the filtering)""",
    )

    # Options to make SIFT provide additional output files:

    # Options to control when SIFT terminates filtering:
    term_number: int | None = shell.arg(
        default=None,
        argstr="-term_number",
        help="""number of streamlines; continue filtering until this number of streamlines remain""",
    )
    term_ratio: float | None = shell.arg(
        default=None,
        argstr="-term_ratio",
        help="""termination ratio; defined as the ratio between reduction in cost function, and reduction in density of streamlines. Smaller values result in more streamlines being filtered out.""",
    )
    term_mu: float | None = shell.arg(
        default=None,
        argstr="-term_mu",
        help="""terminate filtering once the SIFT proportionality coefficient reaches a given value""",
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
        csv: File | bool | None = shell.outarg(
            default=None,
            argstr="-csv",
            path_template="csv.txt",
            help="""output statistics of execution per iteration to a .csv file""",
        )
        out_mu: File | bool | None = shell.outarg(
            default=None,
            argstr="-out_mu",
            path_template="out_mu.txt",
            help="""output the final value of SIFT proportionality coefficient mu to a text file""",
        )
        output_debug: Directory | bool | None = shell.outarg(
            default=None,
            argstr="-output_debug",
            path_template="output_debug",
            help="""write to a directory various output images for assessing & debugging performance etc.""",
        )
        out_selection: File | bool | None = shell.outarg(
            default=None,
            argstr="-out_selection",
            path_template="out_selection.txt",
            help="""output a text file containing the binary selection of streamlines""",
        )
