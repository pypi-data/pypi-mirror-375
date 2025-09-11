# Auto-generated test for dirrotate

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirRotate


@pytest.mark.xfail
def test_dirrotate(tmp_path, cli_parse_only):

    task = DirRotate(
        cartesian=False,
        debug=False,
        force=False,
        in_=File.sample(),
        number=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
