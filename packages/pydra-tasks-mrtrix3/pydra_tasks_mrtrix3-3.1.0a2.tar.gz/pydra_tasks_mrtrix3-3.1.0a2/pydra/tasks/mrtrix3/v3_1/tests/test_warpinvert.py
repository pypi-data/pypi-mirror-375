# Auto-generated test for warpinvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import WarpInvert


@pytest.mark.xfail(reason="Job warpinvert is known not pass yet")
@pytest.mark.xfail
def test_warpinvert(tmp_path, cli_parse_only):

    task = WarpInvert(
        debug=False,
        displacement=False,
        force=False,
        in_=Nifti1.sample(),
        template=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
