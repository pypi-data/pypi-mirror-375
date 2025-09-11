# Auto-generated test for tsfthreshold

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TsfThreshold


@pytest.mark.xfail
def test_tsfthreshold(tmp_path, cli_parse_only):

    task = TsfThreshold(
        T=1.0,
        debug=False,
        force=False,
        in_file=File.sample(),
        invert=False,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
