# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Sh2Peaks(shell.Task["Sh2Peaks.Outputs"]):
    """Peaks of the spherical harmonic function in each voxel are located by commencing a Newton search along each of a set of pre-specified directions

        Within the output image, each successive triplet of volumes encodes the x, y & z components of a 3-vector; their directions in 3D space encode the orientation of the identified peaks, while the norm of each vector encodes the magnitude of the peaks.

        The spherical harmonic coefficients are stored according to the conventions described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/concepts/spherical_harmonics.html


        References
        ----------

            Jeurissen, B.; Leemans, A.; Tournier, J.-D.; Jones, D.K.; Sijbers, J. Investigating the prevalence of complex fiber configurations in white matter tissue with diffusion magnetic resonance imaging. Human Brain Mapping, 2013, 34(11), 2747-2766

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

    executable = "sh2peaks"

    # Arguments
    SH: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image of SH coefficients.""",
    )

    # Options
    num: int | None = shell.arg(
        default=None,
        argstr="-num",
        help="""the number of peaks to extract (default: 3).""",
    )
    direction: MultiInputObj[tuple[float, float]] | None = shell.arg(
        default=None,
        argstr="-direction",
        help="""the direction of a peak to estimate. The algorithm will attempt to find the same number of peaks as have been specified using this option.""",
        sep=" ",
    )
    peaks: ImageIn | None = shell.arg(
        default=None,
        argstr="-peaks",
        help="""the program will try to find the peaks that most closely match those in the image provided.""",
    )
    threshold: float | None = shell.arg(
        default=None,
        argstr="-threshold",
        help="""only peak amplitudes greater than the threshold will be considered.""",
    )
    seeds: File | None = shell.arg(
        default=None,
        argstr="-seeds",
        help="""specify a set of directions from which to start the multiple restarts of the optimisation (by default, the built-in 60 direction set is used)""",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary brain mask image.""",
    )
    fast: bool = shell.arg(
        default=False,
        argstr="-fast",
        help="""use lookup table to compute associated Legendre polynomials (faster, but approximate).""",
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
        out_file: ImageOut = shell.outarg(
            argstr="",
            position=2,
            path_template="out_file.mif",
            help="""the output peaks image""",
        )
