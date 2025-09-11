# Auto-generated test for meshfilter

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MeshFilter


@pytest.mark.xfail
def test_meshfilter(tmp_path, cli_parse_only):

    task = MeshFilter(
        debug=False,
        filter="smooth",
        force=False,
        in_file=File.sample(),
        smooth_influence=None,
        smooth_spatial=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
