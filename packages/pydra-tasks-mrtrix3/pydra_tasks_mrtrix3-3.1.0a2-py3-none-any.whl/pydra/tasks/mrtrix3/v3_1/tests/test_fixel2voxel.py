# Auto-generated test for fixel2voxel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fixel2Voxel


@pytest.mark.xfail
def test_fixel2voxel(tmp_path, cli_parse_only):

    task = Fixel2Voxel(
        debug=False,
        fill=None,
        fixel_in=Nifti1.sample(),
        force=False,
        number=None,
        operation="mean",
        weighted=None,
        image_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
