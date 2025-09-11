# Auto-generated test for warp2metric

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Warp2Metric


@pytest.mark.xfail
def test_warp2metric(tmp_path, cli_parse_only):

    task = Warp2Metric(
        debug=False,
        fc=None,
        force=False,
        in_=Nifti1.sample(),
        jdet=None,
        jmat=None,
    )
    result = task(worker="debug")
    assert not result.errored
