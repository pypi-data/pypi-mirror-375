# Auto-generated test for tckconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckConvert


@pytest.mark.xfail
def test_tckconvert(tmp_path, cli_parse_only):

    task = TckConvert(
        ascii=False,
        debug=False,
        dec=False,
        force=False,
        image2scanner=None,
        increment=None,
        input=File.sample(),
        radius=None,
        scanner2image=None,
        scanner2voxel=None,
        sides=None,
        voxel2scanner=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
