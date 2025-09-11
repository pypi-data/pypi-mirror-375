# Auto-generated test for dirflip

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirFlip


@pytest.mark.xfail
def test_dirflip(tmp_path, cli_parse_only):

    task = DirFlip(
        cartesian=False,
        debug=False,
        force=False,
        in_=File.sample(),
        number=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
