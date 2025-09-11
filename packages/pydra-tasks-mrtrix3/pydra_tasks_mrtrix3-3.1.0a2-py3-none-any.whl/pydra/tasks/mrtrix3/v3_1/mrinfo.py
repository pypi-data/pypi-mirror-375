# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrInfo(shell.Task["MrInfo.Outputs"]):
    """By default, all information contained in each image header will be printed to the console in a reader-friendly format.

        Alternatively, command-line options may be used to extract specific details from the header(s); these are printed to the console in a format more appropriate for scripting purposes or piping to file. If multiple options and/or images are provided, the requested header fields will be printed in the order in which they appear in the help page, with all requested details from each input image in sequence printed before the next image is processed.

        The command can also write the diffusion gradient table from a single input image to file; either in the MRtrix or FSL format (bvecs/bvals file pair; includes appropriate diffusion gradient vector reorientation)

        The -dwgrad, -export_* and -shell_* options provide (information about) the diffusion weighting gradient table after it has been processed by the MRtrix3 back-end (vectors normalised, b-values scaled by the square of the vector norm, depending on the -bvalue_scaling option). To see the raw gradient table information as stored in the image header, i.e. without MRtrix3 back-end processing, use "-property dw_scheme".

        The -bvalue_scaling option controls an aspect of the import of diffusion gradient tables. When the input diffusion-weighting direction vectors have norms that differ substantially from unity, the b-values will be scaled by the square of their corresponding vector norm (this is how multi-shell acquisitions are frequently achieved on scanner platforms). However in some rare instances, the b-values may be correct, despite the vectors not being of unit norm (or conversely, the b-values may need to be rescaled even though the vectors are close to unit norm). This option allows the user to control this operation and override MRrtix3's automatic detection.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: J-Donald Tournier (jdtournier@gmail.com) and Robert E. Smith (robert.smith@florey.edu.au)

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

    executable = "mrinfo"

    # Arguments
    image_: MultiInputObj[ImageIn] = shell.arg(
        argstr="",
        position=1,
        help="""the input image(s).""",
    )

    # Options
    all: bool = shell.arg(
        default=False,
        argstr="-all",
        help="""print all properties, rather than the first and last 2 of each.""",
    )
    name: bool = shell.arg(
        default=False,
        argstr="-name",
        help="""print the file system path of the image""",
    )
    format: bool = shell.arg(
        default=False,
        argstr="-format",
        help="""image file format""",
    )
    ndim: bool = shell.arg(
        default=False,
        argstr="-ndim",
        help="""number of image dimensions""",
    )
    size: bool = shell.arg(
        default=False,
        argstr="-size",
        help="""image size along each axis""",
    )
    spacing: bool = shell.arg(
        default=False,
        argstr="-spacing",
        help="""voxel spacing along each image dimension""",
    )
    datatype: bool = shell.arg(
        default=False,
        argstr="-datatype",
        help="""data type used for image data storage""",
    )
    strides: bool = shell.arg(
        default=False,
        argstr="-strides",
        help="""data strides i.e. order and direction of axes data layout""",
    )
    offset: bool = shell.arg(
        default=False,
        argstr="-offset",
        help="""image intensity offset""",
    )
    multiplier: bool = shell.arg(
        default=False,
        argstr="-multiplier",
        help="""image intensity multiplier""",
    )
    transform: bool = shell.arg(
        default=False,
        argstr="-transform",
        help="""the transformation from image coordinates [mm] to scanner / real world coordinates [mm]""",
    )

    # Options for exporting image header fields:
    property: MultiInputObj[str] | None = shell.arg(
        default=None,
        argstr="-property",
        help="""any text properties embedded in the image header under the specified key (use 'all' to list all keys found)""",
    )

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
    bvalue_scaling: bool = shell.arg(
        default=False,
        argstr="-bvalue_scaling",
        help="""enable or disable scaling of diffusion b-values by the square of the corresponding DW gradient norm (see Desciption). Valid choices are: yes/no, true/false, 0/1 (default: automatic).""",
    )

    # DW gradient table export options:
    dwgrad: bool = shell.arg(
        default=False,
        argstr="-dwgrad",
        help="""the diffusion-weighting gradient table, as interpreted by MRtrix3""",
    )
    shell_bvalues: bool = shell.arg(
        default=False,
        argstr="-shell_bvalues",
        help="""list the average b-value of each shell""",
    )
    shell_sizes: bool = shell.arg(
        default=False,
        argstr="-shell_sizes",
        help="""list the number of volumes in each shell""",
    )
    shell_indices: bool = shell.arg(
        default=False,
        argstr="-shell_indices",
        help="""list the image volumes attributed to each b-value shell""",
    )

    # Options for exporting phase-encode tables:
    petable: bool = shell.arg(
        default=False,
        argstr="-petable",
        help="""print the phase encoding table""",
    )

    # Handling of piped images:
    nodelete: bool = shell.arg(
        default=False,
        argstr="-nodelete",
        help="""don't delete temporary images or images passed to mrinfo via Unix pipes""",
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
        json_keyval: File | bool | None = shell.outarg(
            default=None,
            argstr="-json_keyval",
            path_template="json_keyval.txt",
            help="""export header key/value entries to a JSON file""",
        )
        json_all: File | bool | None = shell.outarg(
            default=None,
            argstr="-json_all",
            path_template="json_all.txt",
            help="""export all header contents to a JSON file""",
        )
        export_grad_mrtrix: File | bool | None = shell.outarg(
            default=None,
            argstr="-export_grad_mrtrix",
            path_template="export_grad_mrtrix.txt",
            help="""export the diffusion-weighted gradient table to file in MRtrix format""",
        )
        export_grad_fsl: tuple[File, File] | bool | None = shell.outarg(
            default=None,
            argstr="-export_grad_fsl",
            path_template=(
                "export_grad_fsl0.txt",
                "export_grad_fsl1.txt",
            ),
            help="""export the diffusion-weighted gradient table to files in FSL (bvecs / bvals) format""",
            sep=" ",
        )
        export_pe_table: File | bool | None = shell.outarg(
            default=None,
            argstr="-export_pe_table",
            path_template="export_pe_table.txt",
            help="""export phase-encoding table to file""",
        )
        export_pe_eddy: tuple[File, File] | bool | None = shell.outarg(
            default=None,
            argstr="-export_pe_eddy",
            path_template=(
                "export_pe_eddy0.txt",
                "export_pe_eddy1.txt",
            ),
            help="""export phase-encoding information to an EDDY-style config / index file pair""",
            sep=" ",
        )
