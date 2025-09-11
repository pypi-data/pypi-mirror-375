# Auto-generated test for mrhistogram

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrHistogram


@pytest.mark.xfail
def test_mrhistogram(tmp_path, cli_parse_only):

    task = MrHistogram(
        allvolumes=False,
        bins=None,
        debug=False,
        force=False,
        ignorezero=False,
        image_=Nifti1.sample(),
        mask=None,
        template=None,
        hist=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
