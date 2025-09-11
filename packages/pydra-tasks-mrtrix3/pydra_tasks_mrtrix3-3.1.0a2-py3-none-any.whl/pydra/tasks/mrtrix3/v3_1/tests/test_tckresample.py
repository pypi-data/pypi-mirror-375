# Auto-generated test for tckresample

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckResample


@pytest.mark.xfail
def test_tckresample(tmp_path, cli_parse_only):

    task = TckResample(
        arc=None,
        debug=False,
        downsample=None,
        endpoints=False,
        force=False,
        in_tracks=Tracks.sample(),
        line=None,
        num_points=None,
        out_tracks=Tracks.sample(),
        step_size=None,
        upsample=None,
    )
    result = task(worker="debug")
    assert not result.errored
