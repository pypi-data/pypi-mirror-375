# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Dwi2Fod(shell.Task["Dwi2Fod.Outputs"]):
    """The spherical harmonic coefficients are stored according to the conventions described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/concepts/spherical_harmonics.html


        Example usages
        --------------


        Perform single-shell single-tissue CSD:

        `$ dwi2fod csd dwi.mif response_wm.txt wmfod.mif`

        This algorithm is designed for single-shell data and only uses a single b-value. The response function text file provided should only contain a a single row, corresponding to the b-value used for CSD.


        Perform multi-shell multi-tissue CSD:

        `$ dwi2fod msmt_csd dwi.mif response_wm.txt wmfod.mif response_gm.txt gm.mif response_csf.txt csf.mif`

        This example is the most common use case of multi-tissue CSD, estimating a white matter FOD, and grey matter and CSF compartments. This algorithm requires at least three unique b-values to estimate three tissue compartments. Each response function text file should have a number of rows equal to the number of b-values used. If only two unique b-values are available, it's also possible to estimate only two tissue compartments, e.g., white matter and CSF.


        References
        ----------

            * If using csd algorithm:
    Tournier, J.-D.; Calamante, F. & Connelly, A. Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. NeuroImage, 2007, 35, 1459-1472

            * If using msmt_csd algorithm:
    Jeurissen, B; Tournier, J-D; Dhollander, T; Connelly, A & Sijbers, J. Multi-tissue constrained spherical deconvolution for improved analysis of multi-shell diffusion MRI data. NeuroImage, 2014, 103, 411-426

            Tournier, J.-D.; Calamante, F., Gadian, D.G. & Connelly, A. Direct estimation of the fiber orientation density function from diffusion-weighted MRI data using spherical deconvolution. NeuroImage, 2004, 23, 1176-1185

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: J-Donald Tournier (jdtournier@gmail.com) and Ben Jeurissen (ben.jeurissen@uantwerpen.be)

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

    executable = "dwi2fod"

    # Arguments
    algorithm: str = shell.arg(
        argstr="",
        position=1,
        help="""the algorithm to use for FOD estimation. (options are: csd,msmt_csd)""",
        allowed_values=["csd", "msmt_csd"],
    )
    dwi: ImageIn = shell.arg(
        argstr="",
        position=2,
        help="""the input diffusion-weighted image""",
    )
    response_odf: MultiInputObj[ty.Any] = shell.arg(
        argstr="",
        position=3,
        help="""pairs of input tissue response and output ODF images""",
    )

    # Options

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

    # DW shell selection options:
    shells: list[float] | None = shell.arg(
        default=None,
        argstr="-shells",
        help="""specify one or more b-values to use during processing, as a comma-separated list of the desired approximate b-values (b-values are clustered to allow for small deviations). Note that some commands are incompatible with multiple b-values, and will report an error if more than one b-value is provided.
WARNING: note that, even though the b=0 volumes are never referred to as a 'shell' in the literature, they still have to be explicitly included in the list of b-values as provided to the -shell option! Several algorithms that include the b=0 volumes in their computations may otherwise return an undesired result.""",
        sep=",",
    )

    # Options common to more than one algorithm:
    directions: File | None = shell.arg(
        default=None,
        argstr="-directions",
        help="""specify the directions over which to apply the non-negativity constraint (by default, the built-in 300 direction set is used). These should be supplied as a text file containing [ az el ] pairs for the directions.""",
    )
    lmax: list[int] | None = shell.arg(
        default=None,
        argstr="-lmax",
        help="""the maximum spherical harmonic order for the output FOD(s).For algorithms with multiple outputs, this should be provided as a comma-separated list of integers, one for each output image; for single-output algorithms, only a single integer should be provided. If omitted, the command will use the lmax of the corresponding response function (i.e based on its number of coefficients), up to a maximum of 8.""",
        sep=",",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary brain mask image.""",
    )

    # Options for the Constrained Spherical Deconvolution algorithm:
    filter: File | None = shell.arg(
        default=None,
        argstr="-filter",
        help="""the linear frequency filtering parameters used for the initial linear spherical deconvolution step (default = [ 1 1 1 0 0 ]). These should be supplied as a text file containing the filtering coefficients for each even harmonic order.""",
    )
    neg_lambda: float | None = shell.arg(
        default=None,
        argstr="-neg_lambda",
        help="""the regularisation parameter lambda that controls the strength of the non-negativity constraint (default = 1).""",
    )
    norm_lambda: float | None = shell.arg(
        default=None,
        argstr="-norm_lambda",
        help="""the regularisation parameter lambda that controls the strength of the constraint on the norm of the solution (default = 1).""",
    )
    threshold: float | None = shell.arg(
        default=None,
        argstr="-threshold",
        help="""the threshold below which the amplitude of the FOD is assumed to be zero, expressed as an absolute amplitude (default = 0).""",
    )
    niter: int | None = shell.arg(
        default=None,
        argstr="-niter",
        help="""the maximum number of iterations to perform for each voxel (default = 50). Use '-niter 0' for a linear unconstrained spherical deconvolution.""",
    )

    # Options for the Multi-Shell, Multi-Tissue Constrained Spherical Deconvolution algorithm:
    norm_lambda: float | None = shell.arg(
        default=None,
        argstr="-norm_lambda",
        help="""the regularisation parameter lambda that controls the strength of the constraint on the norm of the solution (default = 1e-10).""",
    )
    neg_lambda: float | None = shell.arg(
        default=None,
        argstr="-neg_lambda",
        help="""the regularisation parameter lambda that controls the strength of the non-negativity constraint (default = 1e-10).""",
    )

    # Stride options:
    strides: ty.Any = shell.arg(
        default=None,
        argstr="-strides",
        help="""specify the strides of the output data in memory; either as a comma-separated list of (signed) integers, or as a template image from which the strides shall be extracted and used. The actual strides produced will depend on whether the output image format can support it.""",
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
        predicted_signal: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-predicted_signal",
            path_template="predicted_signal.mif",
            help="""output the predicted dwi image.""",
        )
