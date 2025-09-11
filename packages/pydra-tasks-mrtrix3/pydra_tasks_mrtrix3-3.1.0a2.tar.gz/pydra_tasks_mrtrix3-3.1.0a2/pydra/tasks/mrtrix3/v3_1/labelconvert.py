# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class LabelConvert(shell.Task["LabelConvert.Outputs"]):
    """Typical usage is to convert a parcellation image provided by some other software, based on the lookup table provided by that software, to conform to a new lookup table, particularly one where the node indices increment from 1, in preparation for connectome construction; examples of such target lookup table files are provided in share//mrtrix3//labelconvert//, but can be created by the user to provide the desired node set // ordering // colours.

        A more thorough description of the operation and purpose of the labelconvert command can be found in the online documentation:
    https://mrtrix.readthedocs.io/en/3.0.4/quantitative_structural_connectivity/labelconvert_tutorial.html


        Example usages
        --------------


        Convert a Desikan-Killiany parcellation image as provided by FreeSurfer to have nodes incrementing from 1:

        `$ labelconvert aparc+aseg.mgz FreeSurferColorLUT.txt mrtrix3//share//mrtrix3//labelconvert//fs_default.txt nodes.mif`

        Paths to the files in the example above would need to be revised according to their locations on the user's system.


        References
        ----------

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

    executable = "labelconvert"

    # Arguments
    path_in: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image""",
    )
    lut_in: File = shell.arg(
        argstr="",
        position=2,
        help="""the connectome lookup table corresponding to the input image""",
    )
    lut_out: File = shell.arg(
        argstr="",
        position=3,
        help="""the target connectome lookup table for the output image""",
    )

    # Options
    spine: ImageIn | None = shell.arg(
        default=None,
        argstr="-spine",
        help="""provide a manually-defined segmentation of the base of the spine where the streamlines terminate, so that this can become a node in the connection matrix.""",
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
        image_out: ImageOut = shell.outarg(
            argstr="",
            position=4,
            path_template="image_out.mif",
            help="""the output image""",
        )
