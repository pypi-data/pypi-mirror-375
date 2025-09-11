# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Tensor2Metric(shell.Task["Tensor2Metric.Outputs"]):
    """
        References
        ----------

            Basser, P. J.; Mattiello, J. & Lebihan, D. MR diffusion tensor spectroscopy and imaging. Biophysical Journal, 1994, 66, 259-267

            * If using -cl, -cp or -cs options:
    Westin, C. F.; Peled, S.; Gudbjartsson, H.; Kikinis, R. & Jolesz, F. A. Geometrical diffusion measures for MRI from tensor basis analysis. Proc Intl Soc Mag Reson Med, 1997, 5, 1742

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Ben Jeurissen (ben.jeurissen@uantwerpen.be) and Thijs Dhollander (thijs.dhollander@gmail.com) and J-Donald Tournier (jdtournier@gmail.com)

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

    executable = "tensor2metric"

    # Arguments
    tensor: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input tensor image.""",
    )

    # Options
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary brain mask image.""",
    )

    # Diffusion Tensor Imaging:
    num: list[int] | None = shell.arg(
        default=None,
        argstr="-num",
        help="""specify the desired eigenvalue/eigenvector(s). Note that several eigenvalues can be specified as a number sequence. For example, '1,3' specifies the principal (1) and minor (3) eigenvalues/eigenvectors (default = 1).""",
        sep=",",
    )
    modulate: str | None = shell.arg(
        default=None,
        argstr="-modulate",
        help="""specify how to modulate the magnitude of the eigenvectors. Valid choices are: none, FA, eigval (default = FA).""",
        allowed_values=["none", "fa", "eigval"],
    )

    # Diffusion Kurtosis Imaging:
    dkt: ImageIn | None = shell.arg(
        default=None,
        argstr="-dkt",
        help="""input diffusion kurtosis tensor.""",
    )
    mk_dirs: File | None = shell.arg(
        default=None,
        argstr="-mk_dirs",
        help="""specify the directions used to numerically calculate mean kurtosis (by default, the built-in 300 direction set is used). These should be supplied as a text file containing [ az el ] pairs for the directions.""",
    )
    rk_ndirs: int | None = shell.arg(
        default=None,
        argstr="-rk_ndirs",
        help="""specify the number of directions used to numerically calculate radial kurtosis (by default, 300 directions are used).""",
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
        adc: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-adc",
            path_template="adc.mif",
            help="""compute the mean apparent diffusion coefficient (ADC) of the diffusion tensor. (sometimes also referred to as the mean diffusivity (MD))""",
        )
        fa: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-fa",
            path_template="fa.mif",
            help="""compute the fractional anisotropy (FA) of the diffusion tensor.""",
        )
        ad: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-ad",
            path_template="ad.mif",
            help="""compute the axial diffusivity (AD) of the diffusion tensor. (equivalent to the principal eigenvalue)""",
        )
        rd: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-rd",
            path_template="rd.mif",
            help="""compute the radial diffusivity (RD) of the diffusion tensor. (equivalent to the mean of the two non-principal eigenvalues)""",
        )
        value: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-value",
            path_template="value.mif",
            help="""compute the selected eigenvalue(s) of the diffusion tensor.""",
        )
        vector: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-vector",
            path_template="vector.mif",
            help="""compute the selected eigenvector(s) of the diffusion tensor.""",
        )
        cl: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-cl",
            path_template="cl.mif",
            help="""compute the linearity metric of the diffusion tensor. (one of the three Westin shape metrics)""",
        )
        cp: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-cp",
            path_template="cp.mif",
            help="""compute the planarity metric of the diffusion tensor. (one of the three Westin shape metrics)""",
        )
        cs: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-cs",
            path_template="cs.mif",
            help="""compute the sphericity metric of the diffusion tensor. (one of the three Westin shape metrics)""",
        )
        mk: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-mk",
            path_template="mk.mif",
            help="""compute the mean kurtosis (MK) of the kurtosis tensor.""",
        )
        ak: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-ak",
            path_template="ak.mif",
            help="""compute the axial kurtosis (AK) of the kurtosis tensor.""",
        )
        rk: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-rk",
            path_template="rk.mif",
            help="""compute the radial kurtosis (RK) of the kurtosis tensor.""",
        )
