# Auto-generated test for sh2power

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Sh2Power


@pytest.mark.xfail
def test_sh2power(tmp_path, cli_parse_only):

    task = Sh2Power(
        SH=Nifti1.sample(),
        debug=False,
        force=False,
        spectrum=False,
        power=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
