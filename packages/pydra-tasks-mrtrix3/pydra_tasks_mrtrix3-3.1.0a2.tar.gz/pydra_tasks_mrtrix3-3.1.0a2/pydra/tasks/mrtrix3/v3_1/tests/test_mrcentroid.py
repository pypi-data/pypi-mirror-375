# Auto-generated test for mrcentroid

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrCentroid


@pytest.mark.xfail
def test_mrcentroid(tmp_path, cli_parse_only):

    task = MrCentroid(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        mask=None,
        voxelspace=False,
    )
    result = task(worker="debug")
    assert not result.errored
