# Auto-generated test for peaks2fixel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Peaks2Fixel


@pytest.mark.xfail
def test_peaks2fixel(tmp_path, cli_parse_only):

    task = Peaks2Fixel(
        dataname=None,
        debug=False,
        directions=Nifti1.sample(),
        force=False,
        fixels=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
