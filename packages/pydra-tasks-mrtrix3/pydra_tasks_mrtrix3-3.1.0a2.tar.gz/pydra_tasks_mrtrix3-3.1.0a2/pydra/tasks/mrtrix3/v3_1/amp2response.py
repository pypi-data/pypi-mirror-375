# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Amp2Response(shell.Task["Amp2Response.Outputs"]):
    """This command uses the image data from all selected single-fibre voxels concurrently, rather than simply averaging their individual spherical harmonic coefficients. It also ensures that the response function is non-negative, and monotonic (i.e. its amplitude must increase from the fibre direction out to the orthogonal plane).

        If multi-shell data are provided, and one or more b-value shells are not explicitly requested, the command will generate a response function for every b-value shell (including b=0 if present).


        References
        ----------

            Smith, R. E.; Dhollander, T. & Connelly, A. Constrained linear least squares estimation of anisotropic response function for spherical deconvolution. ISMRM Workshop on Breaking the Barriers of Diffusion MRI, 23.

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Robert E. Smith (robert.smith@florey.edu.au) and J-Donald Tournier (jdtournier@gmail.com)

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

    executable = "amp2response"

    # Arguments
    amps: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the amplitudes image""",
    )
    mask: ImageIn = shell.arg(
        argstr="",
        position=2,
        help="""the mask containing the voxels from which to estimate the response function""",
    )
    directions_image: ImageIn = shell.arg(
        argstr="",
        position=3,
        help="""a 4D image containing the estimated fibre directions""",
    )

    # Options
    isotropic: bool = shell.arg(
        default=False,
        argstr="-isotropic",
        help="""estimate an isotropic response function (lmax=0 for all shells)""",
    )
    noconstraint: bool = shell.arg(
        default=False,
        argstr="-noconstraint",
        help="""disable the non-negativity and monotonicity constraints""",
    )
    directions: File | None = shell.arg(
        default=None,
        argstr="-directions",
        help="""provide an external text file containing the directions along which the amplitudes are sampled""",
    )

    # DW shell selection options:
    shells: list[float] | None = shell.arg(
        default=None,
        argstr="-shells",
        help="""specify one or more b-values to use during processing, as a comma-separated list of the desired approximate b-values (b-values are clustered to allow for small deviations). Note that some commands are incompatible with multiple b-values, and will report an error if more than one b-value is provided.
WARNING: note that, even though the b=0 volumes are never referred to as a 'shell' in the literature, they still have to be explicitly included in the list of b-values as provided to the -shell option! Several algorithms that include the b=0 volumes in their computations may otherwise return an undesired result.""",
        sep=",",
    )
    lmax: list[int] | None = shell.arg(
        default=None,
        argstr="-lmax",
        help="""specify the maximum harmonic degree of the response function to estimate (can be a comma-separated list for multi-shell data)""",
        sep=",",
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
        response: File = shell.outarg(
            argstr="",
            position=4,
            path_template="response.txt",
            help="""the output zonal spherical harmonic coefficients""",
        )
