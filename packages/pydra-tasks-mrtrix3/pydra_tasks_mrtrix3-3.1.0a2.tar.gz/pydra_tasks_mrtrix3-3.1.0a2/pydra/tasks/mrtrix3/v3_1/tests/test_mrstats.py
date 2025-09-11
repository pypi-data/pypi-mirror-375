# Auto-generated test for mrstats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrStats


@pytest.mark.xfail(reason="Job mrstats is known not pass yet")
@pytest.mark.xfail
def test_mrstats(tmp_path, cli_parse_only):

    task = MrStats(
        allvolumes=False,
        debug=False,
        force=False,
        ignorezero=False,
        image_=Nifti1.sample(),
        mask=None,
        output=None,
    )
    result = task(worker="debug")
    assert not result.errored
