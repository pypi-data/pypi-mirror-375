# Auto-generated from MRtrix C++ command with '__print_pydra_code__' secret option

import typing as ty
from pathlib import Path  # noqa: F401
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401
from pydra.compose import shell
from pydra.utils.typing import MultiInputObj


@shell.define
class TransformCalc(shell.Task["TransformCalc.Outputs"]):
    """
        Example usages
        --------------


        Invert a transformation:

        `$ transformcalc matrix_in.txt invert matrix_out.txt`



        Calculate the matrix square root of the input transformation (halfway transformation):

        `$ transformcalc matrix_in.txt half matrix_out.txt`



        Calculate the rigid component of an affine input transformation:

        `$ transformcalc affine_in.txt rigid rigid_out.txt`



        Calculate the transformation matrix from an original image and an image with modified header:

        `$ transformcalc orig_image modified_image header output`



        Calculate the average affine matrix of a set of input matrices:

        `$ transformcalc input1.txt ... inputN.txt average matrix_out.txt`



        Create interpolated transformation matrix between two inputs:

        `$ transformcalc input1.txt input2.txt interpolate matrix_out.txt`

        Based on matrix decomposition with linear interpolation of translation, rotation and stretch described in: Shoemake, K., Hill, M., & Duff, T. (1992). Matrix Animation and Polar Decomposition. Matrix, 92, 258-264. doi:10.1.1.56.1336


        Decompose transformation matrix M into translation, rotation and stretch and shear (M = T * R * S):

        `$ transformcalc matrix_in.txt decompose matrixes_out.txt`

        The output is a key-value text file containing: scaling: vector of 3 scaling factors in x, y, z direction; shear: list of shear factors for xy, xz, yz axes; angles: list of Euler angles about static x, y, z axes in radians in the range [0:pi]x[-pi:pi]x[-pi:pi]; angle_axis: angle in radians and rotation axis; translation: translation vector along x, y, z axes in mm; R: composed roation matrix (R = rot_x * rot_y * rot_z); S: composed scaling and shear matrix


        Calculate transformation that aligns two images based on sets of corresponding landmarks:

        `$ transformcalc input moving.txt fixed.txt align_vertices_rigid rigid.txt`

        Similary, 'align_vertices_rigid_scale' produces an affine matrix (rigid and global scale). Vertex coordinates are in scanner space, corresponding vertices must be stored in the same row of moving.txt and fixed.txt. Requires 3 or more vertices in each file. Algorithm: Kabsch 'A solution for the best rotation to relate two sets of vectors' DOI:10.1107/S0567739476001873


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

        Version:3.0.4-1402-gd28b95cd, built Aug 22 2025

        Author: Max Pietsch (maximilian.pietsch@kcl.ac.uk)

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

    executable = "transformcalc"

    # Arguments
    inputs: MultiInputObj[ty.Any] = shell.arg(
        argstr="",
        position=1,
        help="""the input(s) for the specified operation""",
    )
    operation: str = shell.arg(
        argstr="",
        position=2,
        help="""the operation to perform; one of: invert, half, rigid, header, average, interpolate, decompose, align_vertices_rigid, align_vertices_rigid_scale (see description section for details).""",
        allowed_values=[
            "invert",
            "half",
            "rigid",
            "header",
            "average",
            "interpolate",
            "decompose",
            "align_vertices_rigid",
            "align_vertices_rigid_scale",
        ],
    )

    # Options

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
            position=3,
            path_template="out_file.txt",
            help="""the output transformation matrix.""",
        )
