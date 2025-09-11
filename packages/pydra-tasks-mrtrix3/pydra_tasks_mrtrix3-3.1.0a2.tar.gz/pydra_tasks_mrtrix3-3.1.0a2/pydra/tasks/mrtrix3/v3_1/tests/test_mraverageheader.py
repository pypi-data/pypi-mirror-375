# Auto-generated test for mraverageheader

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrAverageheader


@pytest.mark.xfail
def test_mraverageheader(tmp_path, cli_parse_only):

    task = MrAverageheader(
        datatype=None,
        debug=False,
        fill=False,
        force=False,
        in_file=[Nifti1.sample()],
        padding=None,
        spacing=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
