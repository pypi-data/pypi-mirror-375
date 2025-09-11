# Auto-generated test for tsfmult

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TsfMult


@pytest.mark.xfail(reason="Job tsfmult is known not pass yet")
@pytest.mark.xfail
def test_tsfmult(tmp_path, cli_parse_only):

    task = TsfMult(
        debug=False,
        force=False,
        input1=File.sample(),
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
