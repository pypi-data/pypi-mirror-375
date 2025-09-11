# Auto-generated test for warpconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import WarpConvert


@pytest.mark.xfail
def test_warpconvert(tmp_path, cli_parse_only):

    task = WarpConvert(
        debug=False,
        force=False,
        from_=None,
        in_=Nifti1.sample(),
        midway_space=False,
        template=None,
        type="deformation2displacement",
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
