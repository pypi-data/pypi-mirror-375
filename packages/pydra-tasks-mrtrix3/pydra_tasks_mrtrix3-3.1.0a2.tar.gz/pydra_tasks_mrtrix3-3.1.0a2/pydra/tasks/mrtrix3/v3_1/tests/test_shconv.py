# Auto-generated test for shconv

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import ShConv


@pytest.mark.xfail
def test_shconv(tmp_path, cli_parse_only):

    task = ShConv(
        datatype=None,
        debug=False,
        force=False,
        odf_response=[File.sample()],
        strides=None,
        SH_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
