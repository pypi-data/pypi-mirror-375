# Auto-generated test for transformcalc

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TransformCalc


@pytest.mark.xfail
def test_transformcalc(tmp_path, cli_parse_only):

    task = TransformCalc(
        debug=False,
        force=False,
        inputs=[File.sample()],
        operation="invert",
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
