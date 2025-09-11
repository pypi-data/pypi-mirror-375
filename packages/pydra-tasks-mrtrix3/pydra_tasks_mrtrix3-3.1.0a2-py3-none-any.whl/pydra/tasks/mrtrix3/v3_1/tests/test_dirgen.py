# Auto-generated test for dirgen

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirGen


@pytest.mark.xfail
def test_dirgen(tmp_path, cli_parse_only):

    task = DirGen(
        cartesian=False,
        debug=False,
        force=False,
        ndir=1,
        niter=None,
        power=None,
        restarts=None,
        unipolar=False,
        dirs=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
