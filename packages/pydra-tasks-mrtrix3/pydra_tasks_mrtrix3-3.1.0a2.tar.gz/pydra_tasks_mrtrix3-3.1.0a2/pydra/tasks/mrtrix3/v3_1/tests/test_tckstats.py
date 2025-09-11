# Auto-generated test for tckstats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckStats


@pytest.mark.xfail(reason="Job tckstats is known not pass yet")
@pytest.mark.xfail
def test_tckstats(tmp_path, cli_parse_only):

    task = TckStats(
        debug=False,
        force=False,
        ignorezero=False,
        output=None,
        tck_weights_in=None,
        tracks_in=Tracks.sample(),
        dump=None,
        histogram=None,
    )
    result = task(worker="debug")
    assert not result.errored
