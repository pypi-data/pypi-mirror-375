# Auto-generated test for fixelconnectivity

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FixelConnectivity


@pytest.mark.xfail(reason="Job fixelconnectivity is known not pass yet")
@pytest.mark.xfail
def test_fixelconnectivity(tmp_path, cli_parse_only):

    task = FixelConnectivity(
        angle=None,
        debug=False,
        fixel_directory=File.sample(),
        force=False,
        mask=None,
        tck_weights_in=None,
        threshold=None,
        tracks=Tracks.sample(),
        count=None,
        extent=None,
        matrix=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
