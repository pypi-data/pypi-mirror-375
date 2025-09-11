# Auto-generated test for meshconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MeshConvert


@pytest.mark.xfail
def test_meshconvert(tmp_path, cli_parse_only):

    task = MeshConvert(
        binary=False,
        debug=False,
        force=False,
        in_file=File.sample(),
        transform=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
