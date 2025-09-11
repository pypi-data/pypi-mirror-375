# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class Fod2Dec(shell.Task["Fod2Dec.Outputs"]):
    """By default, the FOD-based DEC is weighted by the integral of the FOD. To weight by another scalar map, use the -contrast option. This option can also be used for panchromatic sharpening, e.g., by supplying a T1 (or other sensible) anatomical volume with a higher spatial resolution.


    References
    ----------

        Dhollander T, Smith RE, Tournier JD, Jeurissen B, Connelly A. Time to move on: an FOD-based DEC map to replace DTI's trademark DEC FA. Proc Intl Soc Mag Reson Med, 2015, 23, 1027

        Dhollander T, Raffelt D, Smith RE, Connelly A. Panchromatic sharpening of FOD-based DEC maps by structural T1 information. Proc Intl Soc Mag Reson Med, 2015, 23, 566

        Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


    MRtrix
    ------

    Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

    Author: Thijs Dhollander (thijs.dhollander@gmail.com)

    Copyright: Copyright (C) 2014 The Florey Institute of Neuroscience and Mental Health, Melbourne, Australia. This is free software; see the source for copying conditions. There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    """

    executable = "fod2dec"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=1,
        help="""The input FOD image (spherical harmonic coefficients).""",
    )

    # Options
    mask: ImageIn | None = shell.arg(
        default=None,
        argstr="-mask",
        help="""Only perform DEC computation within the specified mask image.""",
    )
    contrast: ImageIn | None = shell.arg(
        default=None,
        argstr="-contrast",
        help="""Weight the computed DEC map by the provided image contrast. If the contrast has a different image grid, the DEC map is first resliced and renormalised. To achieve panchromatic sharpening, provide an image with a higher spatial resolution than the input FOD image; e.g., a T1 anatomical volume. Only the DEC is subject to the mask, so as to allow for partial colouring of the contrast image.
Default when this option is *not* provided: integral of input FOD, subject to the same mask/threshold as used for DEC computation.""",
    )
    lum: bool = shell.arg(
        default=False,
        argstr="-lum",
        help="""Correct for luminance/perception, using default values Cr,Cg,Cb = 0.3,0.5,0.2 and gamma = 2.2 (*not* correcting is the theoretical equivalent of Cr,Cg,Cb = 1,1,1 and gamma = 2).""",
    )
    lum_coefs: list[float] | None = shell.arg(
        default=None,
        argstr="-lum_coefs",
        help="""The coefficients Cr,Cg,Cb to correct for luminance/perception. Note: this implicitly switches on luminance/perception correction, using a default gamma = 2.2 unless specified otherwise.""",
        sep=",",
    )
    lum_gamma: float | None = shell.arg(
        default=None,
        argstr="-lum_gamma",
        help="""The gamma value to correct for luminance/perception. Note: this implicitly switches on luminance/perception correction, using a default Cr,Cg,Cb = 0.3,0.5,0.2 unless specified otherwise.""",
    )
    threshold: float | None = shell.arg(
        default=None,
        argstr="-threshold",
        help="""FOD amplitudes below the threshold value are considered zero.""",
    )
    no_weight: bool = shell.arg(
        default=False,
        argstr="-no_weight",
        help="""Do not weight the DEC map; just output the unweighted colours. Reslicing and renormalising of colours will still happen when providing the -contrast option as a template.""",
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
            help="""The output DEC image (weighted RGB triplets).""",
        )
