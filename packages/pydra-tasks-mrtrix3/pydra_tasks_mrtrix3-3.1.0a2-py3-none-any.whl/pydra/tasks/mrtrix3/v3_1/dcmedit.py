# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class DcmEdit(shell.Task["DcmEdit.Outputs"]):
    """Note that this command simply replaces the existing values without modifying the DICOM structure in any way. Replacement text will be truncated if it is too long to fit inside the existing tag.

        WARNING: this command will modify existing data! It is recommended to run this command on a copy of the original data set to avoid loss of data.

        Command-line option -anonymise attempts to remove identifiable information by replacing the following tags:
    - any tag with Value Representation PN will be replaced with 'anonymous';
    - tag (0010,0030) PatientBirthDate will be replaced with an empty string.
    WARNING: there is no guarantee that this command will remove all identiable information, since such information may be contained in any number of private vendor-specific tags. You will need to double-check the results independently if you need to ensure anonymity.


        References
        ----------

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

    executable = "dcmedit"

    # Arguments
    file: File = shell.arg(
        argstr="",
        position=1,
        help="""the DICOM file to be edited.""",
    )

    # Options
    anonymise: bool = shell.arg(
        default=False,
        argstr="-anonymise",
        help="""remove identifiable information (see Description).""",
    )
    id: str | None = shell.arg(
        default=None,
        argstr="-id",
        help="""replace all ID tags with string supplied. This consists of tags (0010, 0020) PatientID and (0010, 1000) OtherPatientIDs""",
    )
    tag: MultiInputObj[tuple[ty.Any, ty.Any, ty.Any]] | None = shell.arg(
        default=None,
        argstr="-tag",
        help="""replace specific tag.""",
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
        pass
