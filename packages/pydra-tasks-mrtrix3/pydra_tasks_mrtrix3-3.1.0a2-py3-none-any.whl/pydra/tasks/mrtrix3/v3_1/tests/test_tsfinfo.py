# Auto-generated test for tsfinfo

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TsfInfo


@pytest.mark.xfail
def test_tsfinfo(tmp_path, cli_parse_only):

    task = TsfInfo(
        ascii=None,
        count=False,
        debug=False,
        force=False,
        tracks=[File.sample()],
    )
    result = task(worker="debug")
    assert not result.errored
