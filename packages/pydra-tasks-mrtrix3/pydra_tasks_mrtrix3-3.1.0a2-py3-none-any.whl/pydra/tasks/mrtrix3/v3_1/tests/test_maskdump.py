# Auto-generated test for maskdump

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MaskDump


@pytest.mark.xfail
def test_maskdump(tmp_path, cli_parse_only):

    task = MaskDump(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        out_file=None,
    )
    result = task(worker="debug")
    assert not result.errored
