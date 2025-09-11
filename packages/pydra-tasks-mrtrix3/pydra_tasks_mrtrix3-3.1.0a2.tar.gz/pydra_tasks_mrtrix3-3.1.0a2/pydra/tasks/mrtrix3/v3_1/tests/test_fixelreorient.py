# Auto-generated test for fixelreorient

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FixelReorient


@pytest.mark.xfail(reason="Job fixelreorient is known not pass yet")
@pytest.mark.xfail
def test_fixelreorient(tmp_path, cli_parse_only):

    task = FixelReorient(
        debug=False,
        fixel_in=File.sample(),
        force=False,
        warp=Nifti1.sample(),
        fixel_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
