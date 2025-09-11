# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class DwiExtract(shell.Task["DwiExtract.Outputs"]):
    """
        Example usages
        --------------


        Calculate the mean b=0 image from a 4D DWI series:

        `$ dwiextract dwi.mif - -bzero | mrmath - mean mean_bzero.mif -axis 3`

        The dwiextract command extracts all volumes for which the b-value is (approximately) zero; the resulting 4D image can then be provided to the mrmath command to calculate the mean intensity across volumes for each voxel.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au) and Thijs Dhollander (thijs.dhollander@gmail.com) and Robert E. Smith (robert.smith@florey.edu.au)

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

    executable = "dwiextract"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input DW image.""",
    )

    # Options
    bzero: bool = shell.arg(
        default=False,
        argstr="-bzero",
        help="""Output b=0 volumes (instead of the diffusion weighted volumes, if -singleshell is not specified).""",
    )
    no_bzero: bool = shell.arg(
        default=False,
        argstr="-no_bzero",
        help="""Output only non b=0 volumes (default, if -singleshell is not specified).""",
    )
    singleshell: bool = shell.arg(
        default=False,
        argstr="-singleshell",
        help="""Force a single-shell (single non b=0 shell) output. This will include b=0 volumes, if present. Use with -bzero to enforce presence of b=0 volumes (error if not present) or with -no_bzero to exclude them.""",
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

    # DW shell selection options:
    shells: list[float] | None = shell.arg(
        default=None,
        argstr="-shells",
        help="""specify one or more b-values to use during processing, as a comma-separated list of the desired approximate b-values (b-values are clustered to allow for small deviations). Note that some commands are incompatible with multiple b-values, and will report an error if more than one b-value is provided.
WARNING: note that, even though the b=0 volumes are never referred to as a 'shell' in the literature, they still have to be explicitly included in the list of b-values as provided to the -shell option! Several algorithms that include the b=0 volumes in their computations may otherwise return an undesired result.""",
        sep=",",
    )

    # DW gradient table export options:

    # Options for importing phase-encode tables:
    import_pe_table: File | None = shell.arg(
        default=None,
        argstr="-import_pe_table",
        help="""import a phase-encoding table from file""",
    )
    import_pe_eddy: tuple[File, File] | None = shell.arg(
        default=None,
        argstr="-import_pe_eddy",
        help="""import phase-encoding information from an EDDY-style config / index file pair""",
        sep=" ",
    )

    # Options for selecting volumes based on phase-encoding:
    pe: list[float] | None = shell.arg(
        default=None,
        argstr="-pe",
        help="""select volumes with a particular phase encoding; this can be three comma-separated values (for i,j,k components of vector direction) or four (direction & total readout time)""",
        sep=",",
    )

    # Stride options:
    strides: ty.Any = shell.arg(
        default=None,
        argstr="-strides",
        help="""specify the strides of the output data in memory; either as a comma-separated list of (signed) integers, or as a template image from which the strides shall be extracted and used. The actual strides produced will depend on whether the output image format can support it.""",
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
            help="""the output image (diffusion-weighted volumes by default).""",
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
