# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class DwiDenoise(shell.Task["DwiDenoise.Outputs"]):
    """DWI data denoising and noise map estimation by exploiting data redundancy in the PCA domain using the prior knowledge that the eigenspectrum of random covariance matrices is described by the universal Marchenko-Pastur (MP) distribution. Fitting the MP distribution to the spectrum of patch-wise signal matrices hence provides an estimator of the noise level 'sigma', as was first shown in Veraart et al. (2016) and later improved in Cordero-Grande et al. (2019). This noise level estimate then determines the optimal cut-off for PCA denoising.

        Important note: image denoising must be performed as the first step of the image processing pipeline. The routine will fail if interpolation or smoothing has been applied to the data prior to denoising.

        Note that this function does not correct for non-Gaussian noise biases present in magnitude-reconstructed MRI images. If available, including the MRI phase data can reduce such non-Gaussian biases, and the command now supports complex input data.


        References
        ----------

            Veraart, J.; Novikov, D.S.; Christiaens, D.; Ades-aron, B.; Sijbers, J. & Fieremans, E. Denoising of diffusion MRI using random matrix theory. NeuroImage, 2016, 142, 394-406, doi: 10.1016/j.neuroimage.2016.08.016

            Veraart, J.; Fieremans, E. & Novikov, D.S. Diffusion MRI noise mapping using random matrix theory. Magn. Res. Med., 2016, 76(5), 1582-1593, doi: 10.1002/mrm.26059

            Cordero-Grande, L.; Christiaens, D.; Hutter, J.; Price, A.N.; Hajnal, J.V. Complex diffusion-weighted image estimation via matrix recovery under general noise models. NeuroImage, 2019, 200, 391-404, doi: 10.1016/j.neuroimage.2019.06.039

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Daan Christiaens (daan.christiaens@kcl.ac.uk) and Jelle Veraart (jelle.veraart@nyumc.org) and J-Donald Tournier (jdtournier@gmail.com)

        Copyright: Copyright (c) 2016 New York University, University of Antwerp, and the MRtrix3 contributors

    Permission is hereby granted, free of charge, to any non-commercial entity ('Recipient') obtaining a copy of this software and associated documentation files (the 'Software'), to the Software solely for non-commercial research, including the rights to use, copy and modify the Software, subject to the following conditions:

             1. The above copyright notice and this permission notice shall be included by Recipient in all copies or substantial portions of the Software.

             2. THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIESOF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BELIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF ORIN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

             3. In no event shall NYU be liable for direct, indirect, special, incidental or consequential damages in connection with the Software. Recipient will defend, indemnify and hold NYU harmless from any claims or liability resulting from the use of the Software by recipient.

             4. Neither anything contained herein nor the delivery of the Software to recipient shall be deemed to grant the Recipient any right or licenses under any patents or patent application owned by NYU.

             5. The Software may only be used for non-commercial research and may not be used for clinical care.

             6. Any publication by Recipient of research involving the Software shall cite the references listed below.
    """

    executable = "dwidenoise"

    # Arguments
    dwi: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input diffusion-weighted image.""",
    )

    # Options
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""Only process voxels within the specified binary brain mask image.""",
    )
    extent: list[int] | None = shell.arg(
        default=None,
        argstr="-extent",
        help="""Set the patch size of the denoising filter. By default, the command will select the smallest isotropic patch size that exceeds the number of DW images in the input data, e.g., 5x5x5 for data with <= 125 DWI volumes, 7x7x7 for data with <= 343 DWI volumes, etc.""",
        sep=",",
    )
    datatype: str | None = shell.arg(
        default=None,
        argstr="-datatype",
        help="""Datatype for the eigenvalue decomposition (single or double precision). For complex input data, this will select complex float32 or complex float64 datatypes.""",
        allowed_values=["float32", "float64"],
    )
    estimator: str | None = shell.arg(
        default=None,
        argstr="-estimator",
        help="""Select the noise level estimator (default = Exp2), either:
* Exp1: the original estimator used in Veraart et al. (2016), or
* Exp2: the improved estimator introduced in Cordero-Grande et al. (2019).""",
        allowed_values=["exp1", "exp2"],
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
            position=2,
            path_template="out.mif",
            help="""the output denoised DWI image.""",
        )
        noise: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-noise",
            path_template="noise.mif",
            help="""The output noise map, i.e., the estimated noise level 'sigma' in the data.Note that on complex input data, this will be the total noise level across real and imaginary channels, so a scale factor sqrt(2) applies.""",
        )
        rank: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-rank",
            path_template="rank.mif",
            help="""The selected signal rank of the output denoised image.""",
        )
