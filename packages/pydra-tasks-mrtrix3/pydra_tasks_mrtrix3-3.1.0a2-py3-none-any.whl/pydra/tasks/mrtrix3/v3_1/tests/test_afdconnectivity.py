# Auto-generated test for afdconnectivity

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import AfdConnectivity


@pytest.mark.xfail
def test_afdconnectivity(tmp_path, cli_parse_only):

    task = AfdConnectivity(
        all_fixels=False,
        debug=False,
        force=False,
        image_=Nifti1.sample(),
        tracks=Tracks.sample(),
        wbft=None,
        afd_map=None,
    )
    result = task(worker="debug")
    assert not result.errored
