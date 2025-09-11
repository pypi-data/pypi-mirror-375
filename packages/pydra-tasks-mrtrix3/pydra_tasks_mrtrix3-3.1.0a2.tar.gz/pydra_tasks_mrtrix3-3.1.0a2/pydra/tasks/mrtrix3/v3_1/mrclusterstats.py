# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class MrClusterstats(shell.Task["MrClusterstats.Outputs"]):
    """In some software packages, a column of ones is automatically added to the GLM design matrix; the purpose of this column is to estimate the "global intercept", which is the predicted value of the observed variable if all explanatory variables were to be zero. However there are rare situations where including such a column would not be appropriate for a particular experimental design. Hence, in MRtrix3 statistical inference commands, it is up to the user to determine whether or not this column of ones should be included in their design matrix, and add it explicitly if necessary. The contrast matrix must also reflect the presence of this additional column.


        References
        ----------

            * If not using the -threshold command-line option:
    Smith, S. M. & Nichols, T. E. Threshold-free cluster enhancement: Addressing problems of smoothing, threshold dependence and localisation in cluster inference. NeuroImage, 2009, 44, 83-98

            * If using the -nonstationary option:
    Salimi-Khorshidi, G. Smith, S.M. Nichols, T.E. Adjusting the effect of nonstationarity in cluster-based and TFCE inference. Neuroimage, 2011, 54(3), 2006-19

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: David Raffelt (david.raffelt@florey.edu.au)

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

    executable = "mrclusterstats"

    # Arguments
    in_file: File = shell.arg(
        argstr="",
        position=1,
        help="""a text file containing the file names of the input images, one file per line""",
    )
    design: File = shell.arg(
        argstr="",
        position=2,
        help="""the design matrix""",
    )
    contrast: File = shell.arg(
        argstr="",
        position=3,
        help="""the contrast matrix""",
    )
    mask: ImageIn = shell.arg(
        argstr="",
        position=4,
        help="""a mask used to define voxels included in the analysis.""",
    )
    output: str = shell.arg(
        argstr="",
        position=5,
        help="""the filename prefix for all output.""",
    )

    # Options

    # Options relating to shuffling of data for nonparametric statistical inference:
    notest: bool = shell.arg(
        default=False,
        argstr="-notest",
        help="""don't perform statistical inference; only output population statistics (effect size, stdev etc)""",
    )
    errors: str | None = shell.arg(
        default=None,
        argstr="-errors",
        help="""specify nature of errors for shuffling; options are: ee,ise,both (default: ee)""",
        allowed_values=["ee", "ise", "both"],
    )
    exchange_within: File | None = shell.arg(
        default=None,
        argstr="-exchange_within",
        help="""specify blocks of observations within each of which data may undergo restricted exchange""",
    )
    exchange_whole: File | None = shell.arg(
        default=None,
        argstr="-exchange_whole",
        help="""specify blocks of observations that may be exchanged with one another (for independent and symmetric errors, sign-flipping will occur block-wise)""",
    )
    strong: bool = shell.arg(
        default=False,
        argstr="-strong",
        help="""use strong familywise error control across multiple hypotheses""",
    )
    nshuffles: int | None = shell.arg(
        default=None,
        argstr="-nshuffles",
        help="""the number of shuffles (default: 5000)""",
    )
    permutations: File | None = shell.arg(
        default=None,
        argstr="-permutations",
        help="""manually define the permutations (relabelling). The input should be a text file defining a m x n matrix, where each relabelling is defined as a column vector of size m, and the number of columns n defines the number of permutations. Can be generated with the palm_quickperms function in PALM (http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/PALM). Overrides the -nshuffles option.""",
    )
    nonstationarity: bool = shell.arg(
        default=False,
        argstr="-nonstationarity",
        help="""perform non-stationarity correction""",
    )
    skew_nonstationarity: float | None = shell.arg(
        default=None,
        argstr="-skew_nonstationarity",
        help="""specify the skew parameter for empirical statistic calculation (default for this command is 1)""",
    )
    nshuffles_nonstationarity: int | None = shell.arg(
        default=None,
        argstr="-nshuffles_nonstationarity",
        help="""the number of shuffles to use when precomputing the empirical statistic image for non-stationarity correction (default: 5000)""",
    )
    permutations_nonstationarity: File | None = shell.arg(
        default=None,
        argstr="-permutations_nonstationarity",
        help="""manually define the permutations (relabelling) for computing the emprical statistics for non-stationarity correction. The input should be a text file defining a m x n matrix, where each relabelling is defined as a column vector of size m, and the number of columns n defines the number of permutations. Can be generated with the palm_quickperms function in PALM (http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/PALM). Overrides the -nshuffles_nonstationarity option.""",
    )

    # Options for controlling TFCE behaviour:
    tfce_dh: float | None = shell.arg(
        default=None,
        argstr="-tfce_dh",
        help="""the height increment used in the tfce integration (default: 0.1)""",
    )
    tfce_e: float | None = shell.arg(
        default=None,
        argstr="-tfce_e",
        help="""tfce extent exponent (default: 0.5)""",
    )
    tfce_h: float | None = shell.arg(
        default=None,
        argstr="-tfce_h",
        help="""tfce height exponent (default: 2)""",
    )

    # Options related to the General Linear Model (GLM):
    variance: File | None = shell.arg(
        default=None,
        argstr="-variance",
        help="""define variance groups for the G-statistic; measurements for which the expected variance is equivalent should contain the same index""",
    )
    ftests: File | None = shell.arg(
        default=None,
        argstr="-ftests",
        help="""perform F-tests; input text file should contain, for each F-test, a row containing ones and zeros, where ones indicate the rows of the contrast matrix to be included in the F-test.""",
    )
    fonly: bool = shell.arg(
        default=False,
        argstr="-fonly",
        help="""only assess F-tests; do not perform statistical inference on entries in the contrast matrix""",
    )
    column: MultiInputObj[File] | None = shell.arg(
        default=None,
        argstr="-column",
        help="""add a column to the design matrix corresponding to subject voxel-wise values (note that the contrast matrix must include an additional column for each use of this option); the text file provided via this option should contain a file name for each subject""",
    )

    # Additional options for mrclusterstats:
    threshold: float | None = shell.arg(
        default=None,
        argstr="-threshold",
        help="""the cluster-forming threshold to use for a standard cluster-based analysis. This disables TFCE, which is the default otherwise.""",
    )
    connectivity: bool = shell.arg(
        default=False,
        argstr="-connectivity",
        help="""use 26-voxel-neighbourhood connectivity (Default: 6)""",
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
