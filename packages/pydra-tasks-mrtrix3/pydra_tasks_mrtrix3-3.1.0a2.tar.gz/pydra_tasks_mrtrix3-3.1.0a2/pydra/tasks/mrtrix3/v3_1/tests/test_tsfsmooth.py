# Auto-generated test for tsfsmooth

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TsfSmooth


@pytest.mark.xfail
def test_tsfsmooth(tmp_path, cli_parse_only):

    task = TsfSmooth(
        debug=False,
        force=False,
        in_file=File.sample(),
        stdev=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
