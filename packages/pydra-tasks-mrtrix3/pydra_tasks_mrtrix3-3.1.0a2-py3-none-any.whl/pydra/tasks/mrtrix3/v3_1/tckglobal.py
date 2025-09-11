# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckGlobal(shell.Task["TckGlobal.Outputs"]):
    """This command will reconstruct the global white matter fibre tractogram that best explains the input DWI data, using a multi-tissue spherical convolution model.

        A more thorough description of the operation of global tractography in MRtrix3 can be found in the online documentation:
    https://mrtrix.readthedocs.io/en/3.0.4/quantitative_structural_connectivity/global_tractography.html


        Example usages
        --------------


        Basic example usage:

        `$ tckglobal dwi.mif wmr.txt -riso csfr.txt -riso gmr.txt -mask mask.mif -niter 1e9 -fod fod.mif -fiso fiso.mif tracks.tck`

        dwi.mif is the input image, wmr.txt is an anisotropic1, multi-shell response function for WM, and csfr.txt and gmr.txt are isotropic response functions for CSF and GM. The output tractogram is saved to tracks.tck. Optional output images fod.mif and fiso.mif contain the predicted WM fODF and isotropic tissue fractions of CSF and GM respectively, estimated as part of the global optimization and thus affected by spatial regularization.


        References
        ----------

            Christiaens, D.; Reisert, M.; Dhollander, T.; Sunaert, S.; Suetens, P. & Maes, F. Global tractography of multi-shell diffusion-weighted imaging data using a multi-tissue model. NeuroImage, 2015, 123, 89-101

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Daan Christiaens (daan.christiaens@kcl.ac.uk)

        Copyright: Copyright (C) 2015 KU Leuven, Dept. Electrical Engineering, ESAT/PSI,
    Herestraat 49 box 7003, 3000 Leuven, Belgium

    This is free software; see the source for copying conditions.
    There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    """

    executable = "tckglobal"

    # Arguments
    source: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the image containing the raw DWI data.""",
    )
    response: File = shell.arg(
        argstr="",
        position=2,
        help="""the response of a track segment on the DWI signal.""",
    )
    tracks: Tracks = shell.arg(
        argstr="",
        position=3,
        help="""the output file containing the tracks generated.""",
    )

    # Options

    # Input options:
    grad: File | None = shell.arg(
        default=None,
        argstr="-grad",
        help="""specify the diffusion encoding scheme (required if not supplied in the header).""",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only reconstruct the tractogram within the specified brain mask image.""",
    )
    riso: MultiInputObj[File] | None = shell.arg(
        default=None,
        argstr="-riso",
        help="""set one or more isotropic response functions. (multiple allowed)""",
    )

    # Parameters:
    lmax: int | None = shell.arg(
        default=None,
        argstr="-lmax",
        help="""set the maximum harmonic order for the output series. (default = 8)""",
    )
    length: float | None = shell.arg(
        default=None,
        argstr="-length",
        help="""set the length of the particles (fibre segments). (default = 1mm)""",
    )
    weight: float | None = shell.arg(
        default=None,
        argstr="-weight",
        help="""set the weight by which particles contribute to the model. (default = 0.1)""",
    )
    ppot: float | None = shell.arg(
        default=None,
        argstr="-ppot",
        help="""set the particle potential, i.e., the cost of adding one segment, relative to the particle weight. (default = 0.05)""",
    )
    cpot: float | None = shell.arg(
        default=None,
        argstr="-cpot",
        help="""set the connection potential, i.e., the energy term that drives two segments together. (default = 0.5)""",
    )
    t0: float | None = shell.arg(
        default=None,
        argstr="-t0",
        help="""set the initial temperature of the metropolis hastings optimizer. (default = 0.1)""",
    )
    t1: float | None = shell.arg(
        default=None,
        argstr="-t1",
        help="""set the final temperature of the metropolis hastings optimizer. (default = 0.001)""",
    )
    niter: int | None = shell.arg(
        default=None,
        argstr="-niter",
        help="""set the number of iterations of the metropolis hastings optimizer. (default = 10M)""",
    )

    # Output options:
    noapo: bool = shell.arg(
        default=False,
        argstr="-noapo",
        help="""disable spherical convolution of fODF with apodized PSF, to output a sum of delta functions rather than a sum of aPSFs.""",
    )

    # Advanced parameters, if you really know what you're doing:
    balance: float | None = shell.arg(
        default=None,
        argstr="-balance",
        help="""balance internal and external energy. (default = 0). Negative values give more weight to the internal energy; positive to the external energy.""",
    )
    density: float | None = shell.arg(
        default=None,
        argstr="-density",
        help="""set the desired density of the free Poisson process. (default = 1)""",
    )
    prob: list[float] | None = shell.arg(
        default=None,
        argstr="-prob",
        help="""set the probabilities of generating birth, death, randshift, optshift and connect proposals respectively. (default = 0.25,0.05,0.25,0.1,0.35)""",
        sep=",",
    )
    beta: float | None = shell.arg(
        default=None,
        argstr="-beta",
        help="""set the width of the Hanning interpolation window. (in [0, 1], default = 0).  If used, a mask is required, and this mask must keep at least one voxel distance to the image bounding box.""",
    )
    lambda_: float | None = shell.arg(
        default=None,
        argstr="-lambda",
        help="""set the weight of the internal energy directly. (default = 1). If provided, any value of -balance will be ignored.""",
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
        fod: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-fod",
            path_template="fod.mif",
            help="""Predicted fibre orientation distribution function (fODF). This fODF is estimated as part of the global track optimization, and therefore incorporates the spatial regularization that it imposes. Internally, the fODF is represented as a discrete sum of apodized point spread functions (aPSF) oriented along the directions of all particles in the voxel, used to predict the DWI signal from the particle configuration.""",
        )
        fiso: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-fiso",
            path_template="fiso.mif",
            help="""Predicted isotropic fractions of the tissues for which response functions were provided with -riso. Typically, these are CSF and GM.""",
        )
        eext: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-eext",
            path_template="eext.mif",
            help="""Residual external energy in every voxel.""",
        )
        etrend: File | bool | None = shell.outarg(
            default=None,
            argstr="-etrend",
            path_template="etrend.txt",
            help="""internal and external energy trend and cooling statistics.""",
        )
