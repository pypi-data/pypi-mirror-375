# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrFilter(shell.Task["MrFilter.Outputs"]):
    """The available filters are: fft, gradient, median, smooth, normalise, zclean.

        Each filter has its own unique set of optional parameters.

        For 4D images, each 3D volume is processed independently.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Robert E. Smith (robert.smith@florey.edu.au) and David Raffelt (david.raffelt@florey.edu.au) and J-Donald Tournier (jdtournier@gmail.com)

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

    executable = "mrfilter"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input image.""",
    )
    filter: str = shell.arg(
        argstr="",
        position=2,
        help="""the type of filter to be applied""",
        allowed_values=["fft", "gradient", "median", "smooth", "normalise", "zclean"],
    )

    # Options

    # Options for FFT filter:
    axes: list[int] | None = shell.arg(
        default=None,
        argstr="-axes",
        help="""the axes along which to apply the Fourier Transform. By default, the transform is applied along the three spatial axes. Provide as a comma-separate list of axis indices.""",
        sep=",",
    )
    inverse: bool = shell.arg(
        default=False,
        argstr="-inverse",
        help="""apply the inverse FFT""",
    )
    magnitude: bool = shell.arg(
        default=False,
        argstr="-magnitude",
        help="""output a magnitude image rather than a complex-valued image""",
    )
    rescale: bool = shell.arg(
        default=False,
        argstr="-rescale",
        help="""rescale values so that inverse FFT recovers original values""",
    )
    centre_zero: bool = shell.arg(
        default=False,
        argstr="-centre_zero",
        help="""re-arrange the FFT results so that the zero-frequency component appears in the centre of the image, rather than at the edges""",
    )

    # Options for gradient filter:
    stdev: list[float] | None = shell.arg(
        default=None,
        argstr="-stdev",
        help="""the standard deviation of the Gaussian kernel used to  smooth the input image (in mm). The image is smoothed to reduced large spurious gradients caused by noise. Use this option to override the default stdev of 1 voxel. This can be specified either as a single value to be used for all 3 axes, or as a comma-separated list of 3 values (one for each axis).""",
        sep=",",
    )
    magnitude: bool = shell.arg(
        default=False,
        argstr="-magnitude",
        help="""output the gradient magnitude, rather than the default x,y,z components""",
    )
    scanner: bool = shell.arg(
        default=False,
        argstr="-scanner",
        help="""define the gradient with respect to the scanner coordinate frame of reference.""",
    )

    # Options for median filter:
    extent: list[int] | None = shell.arg(
        default=None,
        argstr="-extent",
        help="""specify extent of median filtering neighbourhood in voxels. This can be specified either as a single value to be used for all 3 axes, or as a comma-separated list of 3 values (one for each axis) (default: 3x3x3).""",
        sep=",",
    )

    # Options for normalisation filter:
    extent: list[int] | None = shell.arg(
        default=None,
        argstr="-extent",
        help="""specify extent of normalisation filtering neighbourhood in voxels.This can be specified either as a single value to be used for all 3 axes,or as a comma-separated list of 3 values (one for each axis) (default: 3x3x3).""",
        sep=",",
    )

    # Options for smooth filter:
    stdev: list[float] | None = shell.arg(
        default=None,
        argstr="-stdev",
        help="""apply Gaussian smoothing with the specified standard deviation. The standard deviation is defined in mm (Default 1 voxel). This can be specified either as a single value to be used for all axes, or as a comma-separated list of the stdev for each axis.""",
        sep=",",
    )
    fwhm: list[float] | None = shell.arg(
        default=None,
        argstr="-fwhm",
        help="""apply Gaussian smoothing with the specified full-width half maximum. The FWHM is defined in mm (Default 1 voxel * 2.3548). This can be specified either as a single value to be used for all axes, or as a comma-separated list of the FWHM for each axis.""",
        sep=",",
    )
    extent: list[int] | None = shell.arg(
        default=None,
        argstr="-extent",
        help="""specify the extent (width) of kernel size in voxels. This can be specified either as a single value to be used for all axes, or as a comma-separated list of the extent for each axis. The default extent is 2 * ceil(2.5 * stdev / voxel_size) - 1.""",
        sep=",",
    )

    # Options for zclean filter:
    zupper: float | None = shell.arg(
        default=None,
        argstr="-zupper",
        help="""define high intensity outliers; default: 2.5""",
    )
    zlower: float | None = shell.arg(
        default=None,
        argstr="-zlower",
        help="""define low intensity outliers; default: 2.5""",
    )
    bridge: int | None = shell.arg(
        default=None,
        argstr="-bridge",
        help="""number of voxels to gap to fill holes in mask; default: 4""",
    )
    maskin: ImageIn | None = shell.arg(
        default=None,
        argstr="-maskin",
        help="""initial mask that defines the maximum spatial extent and the region from which to smaple the intensity range.""",
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
            position=3,
            path_template="out_file.mif",
            help="""the output image.""",
        )
        maskout: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-maskout",
            path_template="maskout.mif",
            help="""Output a refined mask based on a spatially coherent region with normal intensity range.""",
        )
