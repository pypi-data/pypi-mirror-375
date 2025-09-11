# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class FixelConvert(shell.Task["FixelConvert.Outputs"]):
    """Fixel data are stored utilising the fixel directory format described in the main documentation, which can be found at the following link:
    https://mrtrix.readthedocs.io/en/3.0.4/fixel_based_analysis/fixel_directory_format.html


        Example usages
        --------------


        Convert from the old file format to the new directory format:

        `$ fixelconvert old_fixels.msf new_fixels/ -out_size`

        This performs a simple conversion from old to new format, and additionally writes the contents of the "size" field  within old-format fixel images stored using the "FixelMetric" class (likely all of them) as an additional fixel data file.


        Convert multiple files from old to new format, preserving fixel correspondence:

        `$ for_each *.msf : fixelconvert IN NAME_new/ -template template_fixels/`

        In this example, the for_each script is used to execute the fixelconvert command once for each of a series of input files in the old fixel format, generating a new output fixel directory for each. Importantly here though, the -template option is used to ensure that the ordering of fixels within these output directories is identical, such that fixel data files can be exchanged between them (e.g. accumulating fixel data files across subjects into a single template fixel directory


        Convert from the new directory format to the old file format:

        `$ fixelconvert new_fixels/ old_fixels.msf -value parameter.mif -in_size new_fixels/afd.mif`

        Conversion from the new directory format will contain the value 1.0 for all output fixels in both the "size" and "value" fields of the "FixelMetric" class, unless the -in_size and/or -value options are used respectively to indicate which fixel data files should be used as the source(s) of this information.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au) and Robert E. Smith (robert.smith@florey.edu.au)

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

    executable = "fixelconvert"

    # Arguments
    fixel_in: ty.Any = shell.arg(
        argstr="",
        position=1,
        help="""the input fixel file / directory.""",
    )
    fixel_out: ty.Any = shell.arg(
        argstr="",
        position=2,
        help="""the output fixel file / directory.""",
    )

    # Options

    # Options for converting from old to new format:
    name: str | None = shell.arg(
        default=None,
        argstr="-name",
        help="""assign a different name to the value field output (Default: value). Do not include the file extension.""",
    )
    nii: bool = shell.arg(
        default=False,
        argstr="-nii",
        help="""output the index, directions and data file in NIfTI format instead of .mif""",
    )
    out_size: bool = shell.arg(
        default=False,
        argstr="-out_size",
        help="""also output the 'size' field from the old format""",
    )
    template: Directory | None = shell.arg(
        default=None,
        argstr="-template",
        help="""specify an existing fixel directory (in the new format) to which the new output should conform""",
    )

    # Options for converting from new to old format:
    value: File | None = shell.arg(
        default=None,
        argstr="-value",
        help="""nominate the data file to import to the 'value' field in the old format""",
    )
    in_size: File | None = shell.arg(
        default=None,
        argstr="-in_size",
        help="""import data for the 'size' field in the old format""",
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
