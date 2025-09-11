# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrThreshold(shell.Task["MrThreshold.Outputs"]):
    """The threshold value to be applied can be determined in one of a number of ways: if no relevant command-line option is used, the command will automatically determine an optimal threshold; the -abs option provides the threshold value explicitly; the -percentile, -top and -bottom options enable more fine-grained control over how the threshold value is determined.

        The -mask option only influences those image values that contribute toward the determination of the threshold value; once the threshold is determined, it is applied to the entire image, irrespective of use of the -mask option. If you wish for the voxels outside of the specified mask to additionally be excluded from the output mask, this can be achieved by providing the -out_masked option.

        The four operators available through the "-comparison" option ("lt", "le", "ge" and "gt") correspond to: "less-than" (<), "less-than-or-equal" (<=), "greater-than-or-equal" (>=), and "greater-than" (>). This offers fine-grained control over how the thresholding operation will behave in the presence of values equivalent to the threshold. By default,  the command will select voxels with values greater than or equal to the determined threshold ("ge"); unless the -bottom option is used, in which case after a threshold is determined from the relevant lowest-valued image voxels, those voxels with values less than or equal to that threshold ("le") are selected. This provides more fine-grained control than the -invert option; the latter is provided for backwards compatibility, but is equivalent to selection of the opposite comparison within this selection.

        If no output image path is specified, the command will instead write to standard output the determined threshold value.


        References
        ----------

            * If not using any explicit thresholding mechanism:
    Ridgway, G. R.; Omar, R.; Ourselin, S.; Hill, D. L.; Warren, J. D. & Fox, N. C. Issues with threshold masking in voxel-based morphometry of atrophied brains. NeuroImage, 2009, 44, 99-111

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

    executable = "mrthreshold"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image to be thresholded""",
    )

    # Options

    # Threshold determination mechanisms:
    abs: float | None = shell.arg(
        default=None,
        argstr="-abs",
        help="""specify threshold value as absolute intensity""",
    )
    percentile: float | None = shell.arg(
        default=None,
        argstr="-percentile",
        help="""determine threshold based on some percentile of the image intensity distribution""",
    )
    top: int | None = shell.arg(
        default=None,
        argstr="-top",
        help="""determine threshold that will result in selection of some number of top-valued voxels""",
    )
    bottom: int | None = shell.arg(
        default=None,
        argstr="-bottom",
        help="""determine & apply threshold resulting in selection of some number of bottom-valued voxels (note: implies threshold application operator of "le" unless otherwise specified)""",
    )

    # Threshold determination modifiers:
    allvolumes: bool = shell.arg(
        default=False,
        argstr="-allvolumes",
        help="""compute a single threshold for all image volumes, rather than an individual threshold per volume""",
    )
    ignorezero: bool = shell.arg(
        default=False,
        argstr="-ignorezero",
        help="""ignore zero-valued input values during threshold determination""",
    )
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""compute the threshold based only on values within an input mask image""",
    )

    # Threshold application modifiers:
    comparison: str | None = shell.arg(
        default=None,
        argstr="-comparison",
        help="""comparison operator to use when applying the threshold; options are: lt,le,ge,gt (default = "le" for -bottom; "ge" otherwise)""",
        allowed_values=["lt", "le", "ge", "gt"],
    )
    invert: bool = shell.arg(
        default=False,
        argstr="-invert",
        help="""invert the output binary mask (equivalent to flipping the operator; provided for backwards compatibility)""",
    )
    out_masked: bool = shell.arg(
        default=False,
        argstr="-out_masked",
        help="""mask the output image based on the provided input mask image""",
    )
    nan: bool = shell.arg(
        default=False,
        argstr="-nan",
        help="""set voxels that fail the threshold to NaN rather than zero (output image will be floating-point rather than binary)""",
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
        out_file: ImageOut | None = shell.outarg(
            argstr="",
            position=2,
            default=None,
            path_template="out_file.mif",
            help="""the (optional) output binary image mask""",
        )
