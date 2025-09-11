# Auto-generated test for tcktransform

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckTransform


@pytest.mark.xfail
def test_tcktransform(tmp_path, cli_parse_only):

    task = TckTransform(
        debug=False,
        force=False,
        output=Tracks.sample(),
        tracks=Tracks.sample(),
        transform=Nifti1.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
