# Auto-generated test for voxel2mesh

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Voxel2Mesh


@pytest.mark.xfail
def test_voxel2mesh(tmp_path, cli_parse_only):

    task = Voxel2Mesh(
        blocky=False,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        threshold=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
