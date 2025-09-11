# Auto-generated test for mrmetric

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrMetric


@pytest.mark.xfail
def test_mrmetric(tmp_path, cli_parse_only):

    task = MrMetric(
        debug=False,
        force=False,
        image1=Nifti1.sample(),
        image2=Nifti1.sample(),
        interp=None,
        mask1=None,
        mask2=None,
        metric=None,
        nonormalisation=False,
        overlap=False,
        space=None,
    )
    result = task(worker="debug")
    assert not result.errored
