# Auto-generated test for tckinfo

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckInfo


@pytest.mark.xfail
def test_tckinfo(tmp_path, cli_parse_only):

    task = TckInfo(
        count=False,
        debug=False,
        force=False,
        tracks=[Tracks.sample()],
    )
    result = task(worker="debug")
    assert not result.errored
