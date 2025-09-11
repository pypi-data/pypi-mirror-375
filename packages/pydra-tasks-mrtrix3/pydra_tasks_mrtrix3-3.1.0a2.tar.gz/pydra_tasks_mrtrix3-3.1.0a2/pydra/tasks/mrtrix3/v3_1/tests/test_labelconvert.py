# Auto-generated test for labelconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import LabelConvert


@pytest.mark.xfail
def test_labelconvert(tmp_path, cli_parse_only):

    task = LabelConvert(
        debug=False,
        force=False,
        lut_in=File.sample(),
        lut_out=File.sample(),
        path_in=Nifti1.sample(),
        spine=None,
        image_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
