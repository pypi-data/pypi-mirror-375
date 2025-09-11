# Auto-generated test for connectome2tck

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Connectome2Tck


@pytest.mark.xfail
def test_connectome2tck(tmp_path, cli_parse_only):

    task = Connectome2Tck(
        assignments_in=File.sample(),
        debug=False,
        exclusive=False,
        exemplars=None,
        files=None,
        force=False,
        keep_self=False,
        keep_unassigned=False,
        nodes=None,
        prefix_out="a-string",
        prefix_tck_weights_out=None,
        tck_weights_in=None,
        tracks_in=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
