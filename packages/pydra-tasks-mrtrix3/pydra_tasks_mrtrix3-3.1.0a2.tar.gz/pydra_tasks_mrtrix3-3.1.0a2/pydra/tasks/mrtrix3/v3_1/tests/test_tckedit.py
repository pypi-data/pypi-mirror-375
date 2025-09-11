# Auto-generated test for tckedit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckEdit


@pytest.mark.xfail
def test_tckedit(tmp_path, cli_parse_only):

    task = TckEdit(
        debug=False,
        ends_only=False,
        exclude=None,
        force=False,
        include=None,
        include_ordered=None,
        inverse=False,
        mask=None,
        maxlength=None,
        maxweight=None,
        minlength=None,
        minweight=None,
        number=None,
        skip=None,
        tck_weights_in=None,
        tracks_in=[Tracks.sample()],
        tracks_out=Tracks.sample(),
        tck_weights_out=None,
    )
    result = task(worker="debug")
    assert not result.errored
