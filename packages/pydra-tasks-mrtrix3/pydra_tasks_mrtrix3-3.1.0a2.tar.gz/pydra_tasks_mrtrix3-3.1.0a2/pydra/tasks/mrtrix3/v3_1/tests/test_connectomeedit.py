# Auto-generated test for connectomeedit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import ConnectomeEdit


@pytest.mark.xfail
def test_connectomeedit(tmp_path, cli_parse_only):

    task = ConnectomeEdit(
        debug=False,
        force=False,
        input="a-string",
        operation="to_symmetric",
        output="a-string",
    )
    result = task(worker="debug")
    assert not result.errored
