# Auto-generated test for fivettcheck

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettCheck


@pytest.mark.xfail
def test_fivettcheck(tmp_path, cli_parse_only):

    task = FivettCheck(
        debug=False,
        force=False,
        in_file=[Nifti1.sample()],
        voxels=None,
    )
    result = task(worker="debug")
    assert not result.errored
