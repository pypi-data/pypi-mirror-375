# Auto-generated test for mesh2voxel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Mesh2Voxel


@pytest.mark.xfail
def test_mesh2voxel(tmp_path, cli_parse_only):

    task = Mesh2Voxel(
        debug=False,
        force=False,
        source=File.sample(),
        template=Nifti1.sample(),
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
