# Auto-generated test for tcksample

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckSample


@pytest.mark.xfail
def test_tcksample(tmp_path, cli_parse_only):

    task = TckSample(
        debug=False,
        force=False,
        image_=Nifti1.sample(),
        nointerp=False,
        precise=False,
        stat_tck=None,
        tracks=Tracks.sample(),
        use_tdi_fraction=False,
        values=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
