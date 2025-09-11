# Auto-generated test for dwidenoise

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiDenoise


@pytest.mark.xfail
def test_dwidenoise(tmp_path, cli_parse_only):

    task = DwiDenoise(
        datatype=None,
        debug=False,
        dwi=Nifti1.sample(),
        estimator=None,
        extent=None,
        force=False,
        mask=None,
        noise=None,
        out=File.sample(),
        rank=None,
    )
    result = task(worker="debug")
    assert not result.errored
