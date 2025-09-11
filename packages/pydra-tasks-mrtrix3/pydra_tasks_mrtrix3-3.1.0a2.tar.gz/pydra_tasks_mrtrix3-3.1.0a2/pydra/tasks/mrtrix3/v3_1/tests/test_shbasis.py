# Auto-generated test for shbasis

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import ShBasis


@pytest.mark.xfail
def test_shbasis(tmp_path, cli_parse_only):

    task = ShBasis(
        SH=[Nifti1.sample()],
        convert=None,
        debug=False,
        force=False,
    )
    result = task(worker="debug")
    assert not result.errored
