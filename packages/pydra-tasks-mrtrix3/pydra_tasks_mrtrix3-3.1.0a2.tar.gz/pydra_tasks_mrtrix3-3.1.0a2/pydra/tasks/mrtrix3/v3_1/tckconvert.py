# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckConvert(shell.Task["TckConvert.Outputs"]):
    """The program currently supports MRtrix .tck files (input/output), ascii text files (input/output), VTK polydata files (input/output), and RenderMan RIB (export only).


        Example usages
        --------------


        Writing multiple ASCII files, one per streamline:

        `$ tckconvert input.tck output-[].txt`

        By using the multi-file numbering syntax, where square brackets denote the position of the numbering for the files, this example will produce files named output-0000.txt, output-0001.txt, output-0002.txt, ...


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Daan Christiaens (daan.christiaens@kcl.ac.uk) and J-Donald Tournier (jdtournier@gmail.com) and Philip Broser (philip.broser@me.com) and Daniel Blezek (daniel.blezek@gmail.com)

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

    executable = "tckconvert"

    # Arguments
    input: ty.Any = shell.arg(
        argstr="",
        position=1,
        help="""the input track file.""",
    )

    # Options
    scanner2voxel: ImageIn | None = shell.arg(
        default=None,
        argstr="-scanner2voxel",
        help="""if specified, the properties of this image will be used to convert track point positions from real (scanner) coordinates into voxel coordinates.""",
    )
    scanner2image: ImageIn | None = shell.arg(
        default=None,
        argstr="-scanner2image",
        help="""if specified, the properties of this image will be used to convert track point positions from real (scanner) coordinates into image coordinates (in mm).""",
    )
    voxel2scanner: ImageIn | None = shell.arg(
        default=None,
        argstr="-voxel2scanner",
        help="""if specified, the properties of this image will be used to convert track point positions from voxel coordinates into real (scanner) coordinates.""",
    )
    image2scanner: ImageIn | None = shell.arg(
        default=None,
        argstr="-image2scanner",
        help="""if specified, the properties of this image will be used to convert track point positions from image coordinates (in mm) into real (scanner) coordinates.""",
    )

    # Options specific to PLY writer:
    sides: int | None = shell.arg(
        default=None,
        argstr="-sides",
        help="""number of sides for streamlines""",
    )
    increment: int | None = shell.arg(
        default=None,
        argstr="-increment",
        help="""generate streamline points at every (increment) points""",
    )

    # Options specific to RIB writer:
    dec: bool = shell.arg(
        default=False,
        argstr="-dec",
        help="""add DEC as a primvar""",
    )

    # Options for both PLY and RIB writer:
    radius: float | None = shell.arg(
        default=None,
        argstr="-radius",
        help="""radius of the streamlines""",
    )

    # Options specific to VTK writer:
    ascii: bool = shell.arg(
        default=False,
        argstr="-ascii",
        help="""write an ASCII VTK file (binary by default)""",
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
        out_file: File = shell.outarg(
            argstr="",
            position=2,
            path_template="out_file.txt",
            help="""the output track file.""",
        )
