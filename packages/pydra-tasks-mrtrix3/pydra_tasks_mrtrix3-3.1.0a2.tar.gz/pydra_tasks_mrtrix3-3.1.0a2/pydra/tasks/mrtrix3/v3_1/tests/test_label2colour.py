# Auto-generated test for label2colour

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Label2Colour


@pytest.mark.xfail
def test_label2colour(tmp_path, cli_parse_only):

    task = Label2Colour(
        debug=False,
        force=False,
        lut=None,
        nodes_in=Nifti1.sample(),
        colour_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
