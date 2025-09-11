# Auto-generated test for voxel2fixel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Voxel2Fixel


@pytest.mark.xfail(reason="Job voxel2fixel is known not pass yet")
@pytest.mark.xfail
def test_voxel2fixel(tmp_path, cli_parse_only):

    task = Voxel2Fixel(
        debug=False,
        fixel_data_out="a-string",
        fixel_directory_in=File.sample(),
        fixel_directory_out="a-string",
        force=False,
        image_in=Nifti1.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
