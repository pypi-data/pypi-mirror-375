# Auto-generated test for dirstat

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirStat


@pytest.mark.xfail
def test_dirstat(tmp_path, cli_parse_only):

    task = DirStat(
        debug=False,
        dirs=File.sample(),
        force=False,
        fslgrad=None,
        grad=None,
        output=None,
        shells=None,
    )
    result = task(worker="debug")
    assert not result.errored
