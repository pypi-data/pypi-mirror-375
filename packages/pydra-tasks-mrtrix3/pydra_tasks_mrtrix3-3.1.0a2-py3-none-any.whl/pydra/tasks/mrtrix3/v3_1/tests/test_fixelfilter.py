# Auto-generated test for fixelfilter

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FixelFilter


@pytest.mark.xfail(reason="Job fixelfilter is known not pass yet")
@pytest.mark.xfail
def test_fixelfilter(tmp_path, cli_parse_only):

    task = FixelFilter(
        debug=False,
        filter="connect",
        force=False,
        fwhm=None,
        input=File.sample(),
        mask=None,
        matrix=File.sample(),
        minweight=None,
        output=File.sample(),
        threshold_connectivity=None,
        threshold_value=None,
    )
    result = task(worker="debug")
    assert not result.errored
