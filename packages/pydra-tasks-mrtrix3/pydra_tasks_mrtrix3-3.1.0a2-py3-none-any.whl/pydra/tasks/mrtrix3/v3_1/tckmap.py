# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TckMap(shell.Task["TckMap.Outputs"]):
    """The -contrast option controls how a value is derived for each streamline that is subsequently contributed to the image elements intersected by that streamline, and therefore strongly influences the contrast of that image. The permissible values are briefly summarised as follows:

        - tdi: Each streamline effectively contributes a value of unity to the final map (equivalent to the original Track Density Imaging (TDI) method)

        - length: The length of the streamline in mm

        - invlength: The reciprocal of streamline length

        - scalar_map: Values are sampled from a scalar image (which must be provided via -image)

        - scalar_map_count: If a non-zero value is sampled from a scalar image (as provided via -image), the streamline contributes a value of 1, otherwise it contributes 0, such that an image can be produced reflecting the density of streamlines that intersect such an image

        - fod_amp: The amplitudes of a Fibre Orientation Distribution (FOD) image

        - curvature: The curvature of the streamline

        - vector_file: A value for each streamline has been pre-calculated, and these are provided in a text file via the -vector_file option

        A "super-resolution" output image can be generated using the -vox option, whether or not a template image is provided using the -template option. If -template is used in conjunction with -vox, the image axes and FoV will still match that of the template image, but the spatial resolution will differ.

        Note: if you run into limitations with RAM usage, make sure you output the results to a .mif file or .mih / .dat file pair; this will avoid the allocation of an additional buffer to store the output for write-out.


        References
        ----------

            * For TDI or DEC TDI:
    Calamante, F.; Tournier, J.-D.; Jackson, G. D. & Connelly, A. Track-density imaging (TDI): Super-resolution white matter imaging using whole-brain track-density mapping. NeuroImage, 2010, 53, 1233-1243

            * If using -contrast length and -stat_vox mean:
    Pannek, K.; Mathias, J. L.; Bigler, E. D.; Brown, G.; Taylor, J. D. & Rose, S. E. The average pathlength map: A diffusion MRI tractography-derived index for studying brain pathology. NeuroImage, 2011, 55, 133-141

            * If using -dixel option with TDI contrast only:
    Smith, R.E., Tournier, J-D., Calamante, F., Connelly, A. A novel paradigm for automated segmentation of very large whole-brain probabilistic tractography data sets. In proc. ISMRM, 2011, 19, 673

            * If using -dixel option with any other contrast:
    Pannek, K., Raffelt, D., Salvado, O., Rose, S. Incorporating directional information in diffusion tractography derived maps: angular track imaging (ATI). In Proc. ISMRM, 2012, 20, 1912

            * If using -tod option:
    Dhollander, T., Emsell, L., Van Hecke, W., Maes, F., Sunaert, S., Suetens, P. Track Orientation Density Imaging (TODI) and Track Orientation Distribution (TOD) based tractography. NeuroImage, 2014, 94, 312-336

            * If using other contrasts / statistics:
    Calamante, F.; Tournier, J.-D.; Smith, R. E. & Connelly, A. A generalised framework for super-resolution track-weighted imaging. NeuroImage, 2012, 59, 2494-2503

            * If using -precise mapping option:
    Smith, R. E.; Tournier, J.-D.; Calamante, F. & Connelly, A. SIFT: Spherical-deconvolution informed filtering of tractograms. NeuroImage, 2013, 67, 298-312 (Appendix 3)

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

    executable = "tckmap"

    # Arguments
    tracks: File = shell.arg(
        argstr="",
        position=1,
        help="""the input track file.""",
    )

    # Options

    # Options for the header of the output image:
    template: ImageIn | None = shell.arg(
        default=None,
        argstr="-template",
        help="""an image file to be used as a template for the output (the output image will have the same transform and field of view).""",
    )
    vox: list[float] | None = shell.arg(
        default=None,
        argstr="-vox",
        help="""provide either an isotropic voxel size (in mm), or comma-separated list of 3 voxel dimensions.""",
        sep=",",
    )
    datatype: str | None = shell.arg(
        default=None,
        argstr="-datatype",
        help="""specify output image data type.""",
        allowed_values=[
            "float16",
            "float16le",
            "float16be",
            "float32",
            "float32le",
            "float32be",
            "float64",
            "float64le",
            "float64be",
            "int64",
            "uint64",
            "int64le",
            "uint64le",
            "int64be",
            "uint64be",
            "int32",
            "uint32",
            "int32le",
            "uint32le",
            "int32be",
            "uint32be",
            "int16",
            "uint16",
            "int16le",
            "uint16le",
            "int16be",
            "uint16be",
            "cfloat16",
            "cfloat16le",
            "cfloat16be",
            "cfloat32",
            "cfloat32le",
            "cfloat32be",
            "cfloat64",
            "cfloat64le",
            "cfloat64be",
            "int8",
            "uint8",
            "bit",
        ],
    )

    # Options for the dimensionality of the output image:
    dec: bool = shell.arg(
        default=False,
        argstr="-dec",
        help="""perform track mapping in directionally-encoded colour (DEC) space""",
    )
    dixel: ty.Any = shell.arg(
        default=None,
        argstr="-dixel",
        help="""map streamlines to dixels within each voxel; requires either a number of dixels (references an internal direction set), or a path to a text file containing a set of directions stored as azimuth/elevation pairs""",
    )
    tod: int | None = shell.arg(
        default=None,
        argstr="-tod",
        help="""generate a Track Orientation Distribution (TOD) in each voxel; need to specify the maximum spherical harmonic degree lmax to use when generating Apodised Point Spread Functions""",
    )

    # Options for the TWI image contrast properties:
    contrast: str | None = shell.arg(
        default=None,
        argstr="-contrast",
        help="""define the desired form of contrast for the output image; options are: tdi, length, invlength, scalar_map, scalar_map_count, fod_amp, curvature, vector_file (default: tdi)""",
        allowed_values=[
            "tdi",
            "length",
            "invlength",
            "scalar_map",
            "scalar_map_count",
            "fod_amp",
            "curvature",
            "vector_file",
        ],
    )
    image_: ImageIn | None = shell.arg(
        default=None,
        argstr="-image",
        help="""provide the scalar image map for generating images with 'scalar_map' / 'scalar_map_count' contrast, or the spherical harmonics image for 'fod_amp' contrast""",
    )
    vector_file: File | None = shell.arg(
        default=None,
        argstr="-vector_file",
        help="""provide the vector data file for generating images with 'vector_file' contrast""",
    )
    stat_vox: str | None = shell.arg(
        default=None,
        argstr="-stat_vox",
        help="""define the statistic for choosing the final voxel intensities for a given contrast type given the individual values from the tracks passing through each voxel. Options are: sum, min, mean, max (default: sum)""",
        allowed_values=["sum", "min", "mean", "max"],
    )
    stat_tck: str | None = shell.arg(
        default=None,
        argstr="-stat_tck",
        help="""define the statistic for choosing the contribution to be made by each streamline as a function of the samples taken along their lengths. Only has an effect for 'scalar_map', 'fod_amp' and 'curvature' contrast types. Options are: sum, min, mean, max, median, mean_nonzero, gaussian, ends_min, ends_mean, ends_max, ends_prod (default: mean)""",
        allowed_values=[
            "sum",
            "min",
            "mean",
            "max",
            "median",
            "mean_nonzero",
            "gaussian",
            "ends_min",
            "ends_mean",
            "ends_max",
            "ends_prod",
        ],
    )
    fwhm_tck: float | None = shell.arg(
        default=None,
        argstr="-fwhm_tck",
        help="""when using gaussian-smoothed per-track statistic, specify the desired full-width half-maximum of the Gaussian smoothing kernel (in mm)""",
    )
    map_zero: bool = shell.arg(
        default=False,
        argstr="-map_zero",
        help="""if a streamline has zero contribution based on the contrast & statistic, typically it is not mapped; use this option to still contribute to the map even if this is the case (these non-contributing voxels can then influence the mean value in each voxel of the map)""",
    )
    backtrack: bool = shell.arg(
        default=False,
        argstr="-backtrack",
        help="""when using -stat_tck ends_*, if the streamline endpoint is outside the FoV, backtrack along the streamline trajectory until an appropriate point is found""",
    )

    # Options for the streamline-to-voxel mapping mechanism:
    upsample: int | None = shell.arg(
        default=None,
        argstr="-upsample",
        help="""upsample the tracks by some ratio using Hermite interpolation before mappping (if omitted, an appropriate ratio will be determined automatically)""",
    )
    precise: bool = shell.arg(
        default=False,
        argstr="-precise",
        help="""use a more precise streamline mapping strategy, that accurately quantifies the length through each voxel (these lengths are then taken into account during TWI calculation)""",
    )
    ends_only: bool = shell.arg(
        default=False,
        argstr="-ends_only",
        help="""only map the streamline endpoints to the image""",
    )
    tck_weights_in: File | None = shell.arg(
        default=None,
        argstr="-tck_weights_in",
        help="""specify a text scalar file containing the streamline weights""",
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
            help="""the output track-weighted image""",
        )
