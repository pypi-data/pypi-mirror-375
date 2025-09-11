# Auto-generated test for fixel2peaks

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fixel2Peaks


@pytest.mark.xfail
def test_fixel2peaks(tmp_path, cli_parse_only):

    task = Fixel2Peaks(
        debug=False,
        force=False,
        in_=File.sample(),
        nan=False,
        number=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
