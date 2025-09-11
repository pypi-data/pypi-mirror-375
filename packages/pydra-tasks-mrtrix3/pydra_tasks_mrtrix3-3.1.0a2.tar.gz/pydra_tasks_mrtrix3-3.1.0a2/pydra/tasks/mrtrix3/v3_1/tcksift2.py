# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckSift2(shell.Task["TckSift2.Outputs"]):
    """
        References
        ----------

            Smith, R. E.; Tournier, J.-D.; Calamante, F. & Connelly, A. SIFT2: Enabling dense quantitative assessment of brain white matter connectivity using streamlines tractography. NeuroImage, 2015, 119, 338-351

            * If using the -linear option:
    Smith, RE; Raffelt, D; Tournier, J-D; Connelly, A. Quantitative Streamlines Tractography: Methods and Inter-Subject Normalisation. Open Science Framework, https://doi.org/10.31219/osf.io/c67kn.

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

    executable = "tcksift2"

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

    # Options

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

    # Regularisation options for SIFT2:
    reg_tikhonov: float | None = shell.arg(
        default=None,
        argstr="-reg_tikhonov",
        help="""provide coefficient for regularising streamline weighting coefficients (Tikhonov regularisation) (default: 0)""",
    )
    reg_tv: float | None = shell.arg(
        default=None,
        argstr="-reg_tv",
        help="""provide coefficient for regularising variance of streamline weighting coefficient to fixels along its length (Total Variation regularisation) (default: 0.1)""",
    )

    # Options for controlling the SIFT2 optimisation algorithm:
    min_td_frac: float | None = shell.arg(
        default=None,
        argstr="-min_td_frac",
        help="""minimum fraction of the FOD integral reconstructed by streamlines; if the reconstructed streamline density is below this fraction, the fixel is excluded from optimisation (default: 0.1)""",
    )
    min_iters: int | None = shell.arg(
        default=None,
        argstr="-min_iters",
        help="""minimum number of iterations to run before testing for convergence; this can prevent premature termination at early iterations if the cost function increases slightly (default: 10)""",
    )
    max_iters: int | None = shell.arg(
        default=None,
        argstr="-max_iters",
        help="""maximum number of iterations to run before terminating program""",
    )
    min_factor: float | None = shell.arg(
        default=None,
        argstr="-min_factor",
        help="""minimum weighting factor for an individual streamline; if the factor falls below this number, the streamline will be rejected entirely (factor set to zero) (default: 0)""",
    )
    min_coeff: float | None = shell.arg(
        default=None,
        argstr="-min_coeff",
        help="""minimum weighting coefficient for an individual streamline; similar to the '-min_factor' option, but using the exponential coefficient basis of the SIFT2 model; these parameters are related as: factor = e^(coeff). Note that the -min_factor and -min_coeff options are mutually exclusive; you can only provide one. (default: -inf)""",
    )
    max_factor: float | None = shell.arg(
        default=None,
        argstr="-max_factor",
        help="""maximum weighting factor that can be assigned to any one streamline (default: inf)""",
    )
    max_coeff: float | None = shell.arg(
        default=None,
        argstr="-max_coeff",
        help="""maximum weighting coefficient for an individual streamline; similar to the '-max_factor' option, but using the exponential coefficient basis of the SIFT2 model; these parameters are related as: factor = e^(coeff). Note that the -max_factor and -max_coeff options are mutually exclusive; you can only provide one. (default: inf)""",
    )
    max_coeff_step: float | None = shell.arg(
        default=None,
        argstr="-max_coeff_step",
        help="""maximum change to a streamline's weighting coefficient in a single iteration (default: 1)""",
    )
    min_cf_decrease: float | None = shell.arg(
        default=None,
        argstr="-min_cf_decrease",
        help="""minimum decrease in the cost function (as a fraction of the initial value) that must occur each iteration for the algorithm to continue (default: 2.5e-05)""",
    )
    linear: bool = shell.arg(
        default=False,
        argstr="-linear",
        help="""perform a linear estimation of streamline weights, rather than the standard non-linear optimisation (typically does not provide as accurate a model fit; but only requires a single pass)""",
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
        out_weights: File = shell.outarg(
            argstr="",
            position=3,
            path_template="out_weights.txt",
            help="""output text file containing the weighting factor for each streamline""",
        )
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
        out_coeffs: File | bool | None = shell.outarg(
            default=None,
            argstr="-out_coeffs",
            path_template="out_coeffs.txt",
            help="""output text file containing the weighting coefficient for each streamline""",
        )
