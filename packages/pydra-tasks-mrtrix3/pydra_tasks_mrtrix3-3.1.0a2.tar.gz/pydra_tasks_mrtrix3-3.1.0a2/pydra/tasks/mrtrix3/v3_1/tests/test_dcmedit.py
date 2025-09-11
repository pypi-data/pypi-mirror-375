# Auto-generated test for dcmedit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DcmEdit


@pytest.mark.xfail
def test_dcmedit(tmp_path, cli_parse_only):

    task = DcmEdit(
        anonymise=False,
        debug=False,
        file=File.sample(),
        force=False,
        id=None,
        tag=None,
    )
    result = task(worker="debug")
    assert not result.errored
