# Auto-generated test for tck2fixel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Tck2Fixel


@pytest.mark.xfail(reason="Job tck2fixel is known not pass yet")
@pytest.mark.xfail
def test_tck2fixel(tmp_path, cli_parse_only):

    task = Tck2Fixel(
        angle=None,
        debug=False,
        fixel_data_out="a-string",
        fixel_folder_in=File.sample(),
        fixel_folder_out="a-string",
        force=False,
        tracks=Tracks.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
