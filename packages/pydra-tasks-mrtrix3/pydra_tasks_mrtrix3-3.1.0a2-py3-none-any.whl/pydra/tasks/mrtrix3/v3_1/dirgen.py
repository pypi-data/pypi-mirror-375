# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class DirGen(shell.Task["DirGen.Outputs"]):
    """Directions are distributed by analogy to an electrostatic repulsion system, with each direction corresponding to a single electrostatic charge (for -unipolar), or a pair of diametrically opposed charges (for the default bipolar case). The energy of the system is determined based on the Coulomb repulsion, which assumes the form 1/r^power, where r is the distance between any pair of charges, and p is the power assumed for the repulsion law (default: 1). The minimum energy state is obtained by gradient descent.


        References
        ----------

            Jones, D.; Horsfield, M. & Simmons, A. Optimal strategies for measuring diffusion in anisotropic systems by magnetic resonance imaging. Magnetic Resonance in Medicine, 1999, 42: 515-525

            Papadakis, N. G.; Murrills, C. D.; Hall, L. D.; Huang, C. L.-H. & Adrian Carpenter, T. Minimal gradient encoding for robust estimation of diffusion anisotropy. Magnetic Resonance Imaging, 2000, 18: 671-679

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

    executable = "dirgen"

    # Arguments
    ndir: int = shell.arg(
        argstr="",
        position=1,
        help="""the number of directions to generate.""",
    )

    # Options
    power: int | None = shell.arg(
        default=None,
        argstr="-power",
        help="""specify exponent to use for repulsion power law (default: 1). This must be a power of 2 (i.e. 1, 2, 4, 8, 16, ...).""",
    )
    niter: int | None = shell.arg(
        default=None,
        argstr="-niter",
        help="""specify the maximum number of iterations to perform (default: 10000).""",
    )
    restarts: int | None = shell.arg(
        default=None,
        argstr="-restarts",
        help="""specify the number of restarts to perform (default: 10).""",
    )
    unipolar: bool = shell.arg(
        default=False,
        argstr="-unipolar",
        help="""optimise assuming a unipolar electrostatic repulsion model rather than the bipolar model normally assumed in DWI""",
    )
    cartesian: bool = shell.arg(
        default=False,
        argstr="-cartesian",
        help="""Output the directions in Cartesian coordinates [x y z] instead of [az el].""",
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
        dirs: File = shell.outarg(
            argstr="",
            position=2,
            path_template="dirs.txt",
            help="""the text file to write the directions to, as [ az el ] pairs.""",
        )
