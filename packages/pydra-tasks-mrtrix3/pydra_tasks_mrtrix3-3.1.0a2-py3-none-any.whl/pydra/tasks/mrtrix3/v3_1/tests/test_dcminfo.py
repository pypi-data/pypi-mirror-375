# Auto-generated test for dcminfo

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DcmInfo


@pytest.mark.xfail
def test_dcminfo(tmp_path, cli_parse_only):

    task = DcmInfo(
        all=False,
        csa=False,
        debug=False,
        file=File.sample(),
        force=False,
        phoenix=False,
        tag=None,
    )
    result = task(worker="debug")
    assert not result.errored
