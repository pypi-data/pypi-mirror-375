# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Dwi2Tensor(shell.Task["Dwi2Tensor.Outputs"]):
    """By default, the diffusion tensor (and optionally the kurtosis tensor) is fitted to the log-signal in two steps: firstly, using weighted least-squares (WLS) with weights based on the empirical signal intensities; secondly, by further iterated weighted least-squares (IWLS) with weights determined by the signal predictions from the previous iteration (by default, 2 iterations will be performed). This behaviour can be altered in two ways:

        * The -ols option will cause the first fitting step to be performed using ordinary least-squares (OLS); that is, all measurements contribute equally to the fit, instead of the default behaviour of weighting based on the empirical signal intensities.

        * The -iter option controls the number of iterations of the IWLS prodedure. If this is set to zero, then the output model parameters will be those resulting from the first fitting step only: either WLS by default, or OLS if the -ols option is used in conjunction with -iter 0.

        By default, the diffusion tensor (and optionally the kurtosis tensor) is fitted using unconstrained optimization. This can result in unexpected diffusion parameters, e.g. parameters that represent negative apparent diffusivities or negative apparent kurtoses, or parameters that correspond to non-monotonic decay of the predicted signal. By supplying the -constrain option, constrained optimization is performed instead and such physically implausible parameters can be avoided. Depending on the presence of the -dkt option, the -constrain option will enforce the following constraints:

        * Non-negative apparent diffusivity (always).

        * Non-negative apparent kurtosis (when the -dkt option is provided).

        * Monotonic signal decay in the b = [0 b_max] range (when the -dkt option is provided).

        The tensor coefficients are stored in the output image as follows:
    volumes 0-5: D11, D22, D33, D12, D13, D23

        If diffusion kurtosis is estimated using the -dkt option, these are stored as follows:
    volumes 0-2: W1111, W2222, W3333
    volumes 3-8: W1112, W1113, W1222, W1333, W2223, W2333
    volumes 9-11: W1122, W1133, W2233
    volumes 12-14: W1123, W1223, W1233


        References
        ----------

            References based on fitting algorithm used:

            * OLS, WLS:
    Basser, P.J.; Mattiello, J.; LeBihan, D. Estimation of the effective self-diffusion tensor from the NMR spin echo. J Magn Reson B., 1994, 103, 247–254.

            * IWLS:
    Veraart, J.; Sijbers, J.; Sunaert, S.; Leemans, A. & Jeurissen, B. Weighted linear least squares estimation of diffusion MRI parameters: strengths, limitations, and pitfalls. NeuroImage, 2013, 81, 335-346

            * any of above with constraints:
    Morez, J.; Szczepankiewicz, F; den Dekker, A. J.; Vanhevel, F.; Sijbers, J. &  Jeurissen, B. Optimal experimental design and estimation for q-space trajectory imaging. Human Brain Mapping, 2023, 44, 1793-1809

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Ben Jeurissen (ben.jeurissen@uantwerpen.be)

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

    executable = "dwi2tensor"

    # Arguments
    dwi: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input dwi image.""",
    )

    # Options
    ols: bool = shell.arg(
        default=False,
        argstr="-ols",
        help="""perform initial fit using an ordinary least-squares (OLS) fit (see Description).""",
    )
    iter: int | None = shell.arg(
        default=None,
        argstr="-iter",
        help="""number of iterative reweightings for IWLS algorithm (default: 2) (see Description).""",
    )
    constrain: bool = shell.arg(
        default=False,
        argstr="-constrain",
        help="""constrain fit to non-negative diffusivity and kurtosis as well as monotonic signal decay (see Description).""",
    )
    directions: File | None = shell.arg(
        default=None,
        argstr="-directions",
        help="""specify the directions along which to apply the constraints (by default, the built-in 300 direction set is used). These should be supplied as a text file containing [ az el ] pairs for the directions.""",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary brain mask image.""",
    )

    # DW gradient table import options:
    grad: File | None = shell.arg(
        default=None,
        argstr="-grad",
        help="""Provide the diffusion-weighted gradient scheme used in the acquisition in a text file. This should be supplied as a 4xN text file with each line in the format [ X Y Z b ], where [ X Y Z ] describe the direction of the applied gradient, and b gives the b-value in units of s/mm^2. If a diffusion gradient scheme is present in the input image header, the data provided with this option will be instead used.""",
    )
    fslgrad: tuple[File, File] | None = shell.arg(
        default=None,
        argstr="-fslgrad",
        help="""Provide the diffusion-weighted gradient scheme used in the acquisition in FSL bvecs/bvals format files. If a diffusion gradient scheme is present in the input image header, the data provided with this option will be instead used.""",
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
        dt: ImageOut = shell.outarg(
            argstr="",
            position=2,
            path_template="dt.mif",
            help="""the output dt image.""",
        )
        b0: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-b0",
            path_template="b0.mif",
            help="""the output b0 image.""",
        )
        dkt: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-dkt",
            path_template="dkt.mif",
            help="""the output dkt image.""",
        )
        predicted_signal: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-predicted_signal",
            path_template="predicted_signal.mif",
            help="""the predicted dwi image.""",
        )
