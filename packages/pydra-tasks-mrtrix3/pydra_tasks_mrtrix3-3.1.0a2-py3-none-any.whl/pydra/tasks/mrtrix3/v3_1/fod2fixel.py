# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Fod2Fixel(shell.Task["Fod2Fixel.Outputs"]):
    """
        References
        ----------

            * Reference for the FOD segmentation method:
    Smith, R. E.; Tournier, J.-D.; Calamante, F. & Connelly, A. SIFT: Spherical-deconvolution informed filtering of tractograms. NeuroImage, 2013, 67, 298-312 (Appendix 2)

            * Reference for Apparent Fibre Density (AFD):
    Raffelt, D.; Tournier, J.-D.; Rose, S.; Ridgway, G.R.; Henderson, R.; Crozier, S.; Salvado, O.; Connelly, A. Apparent Fibre Density: a novel measure for the analysis of diffusion-weighted magnetic resonance images.Neuroimage, 2012, 15;59(4), 3976-94

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

    executable = "fod2fixel"

    # Arguments
    fod: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""the input fod image.""",
    )

    # Options

    # Metric values for fixel-based sparse output images:

    # FOD FMLS segmenter options:
    fmls_integral: float | None = shell.arg(
        default=None,
        argstr="-fmls_integral",
        help="""threshold absolute numerical integral of positive FOD lobes. Any lobe for which the integral is smaller than this threshold will be discarded. Default: 0.""",
    )
    fmls_peak_value: float | None = shell.arg(
        default=None,
        argstr="-fmls_peak_value",
        help="""threshold peak amplitude of positive FOD lobes. Any lobe for which the maximal peak amplitude is smaller than this threshold will be discarded. Default: 0.1.""",
    )
    fmls_no_thresholds: bool = shell.arg(
        default=False,
        argstr="-fmls_no_thresholds",
        help="""disable all FOD lobe thresholding; every lobe where the FOD is positive will be retained.""",
    )
    fmls_lobe_merge_ratio: float | None = shell.arg(
        default=None,
        argstr="-fmls_lobe_merge_ratio",
        help="""Specify the ratio between a given FOD amplitude sample between two lobes, and the smallest peak amplitude of the adjacent lobes, above which those lobes will be merged. This is the amplitude of the FOD at the 'bridge' point between the two lobes, divided by the peak amplitude of the smaller of the two adjoining lobes. A value of 1.0 will never merge two lobes into one; a value of 0.0 will always merge lobes unless they are bisected by a zero-valued crossing. Default: 1.""",
    )

    # Other options for fod2fixel:
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""only perform computation within the specified binary brain mask image.""",
    )
    maxnum: int | None = shell.arg(
        default=None,
        argstr="-maxnum",
        help="""maximum number of fixels to output for any particular voxel (default: no limit)""",
    )
    nii: bool = shell.arg(
        default=False,
        argstr="-nii",
        help="""output the directions and index file in nii format (instead of the default mif)""",
    )
    dirpeak: bool = shell.arg(
        default=False,
        argstr="-dirpeak",
        help="""define the fixel direction as that of the lobe's maximal peak as opposed to its weighted mean direction (the default)""",
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
        fixel_directory: Directory = shell.outarg(
            argstr="",
            position=2,
            path_template="fixel_directory",
            help="""the output fixel directory""",
        )
        afd: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-afd",
            path_template="afd.mif",
            help="""output the total Apparent Fibre Density per fixel (integral of FOD lobe)""",
        )
        peak_amp: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-peak_amp",
            path_template="peak_amp.mif",
            help="""output the amplitude of the FOD at the maximal peak per fixel""",
        )
        disp: ImageOut | bool | None = shell.outarg(
            default=None,
            argstr="-disp",
            path_template="disp.mif",
            help="""output a measure of dispersion per fixel as the ratio between FOD lobe integral and maximal peak amplitude""",
        )
