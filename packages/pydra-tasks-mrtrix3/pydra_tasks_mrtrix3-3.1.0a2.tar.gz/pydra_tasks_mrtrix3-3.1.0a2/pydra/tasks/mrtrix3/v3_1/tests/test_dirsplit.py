# Auto-generated test for dirsplit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirSplit


@pytest.mark.xfail(reason="Job dirsplit is known not pass yet")
@pytest.mark.xfail
def test_dirsplit(tmp_path, cli_parse_only):

    task = DirSplit(
        cartesian=False,
        debug=False,
        dirs=File.sample(),
        force=False,
        number=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
