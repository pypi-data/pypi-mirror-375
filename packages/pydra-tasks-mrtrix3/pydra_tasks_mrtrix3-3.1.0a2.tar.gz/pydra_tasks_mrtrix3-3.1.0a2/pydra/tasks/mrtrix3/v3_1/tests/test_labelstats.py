# Auto-generated test for labelstats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import LabelStats


@pytest.mark.xfail
def test_labelstats(tmp_path, cli_parse_only):

    task = LabelStats(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        output=None,
        voxelspace=False,
    )
    result = task(worker="debug")
    assert not result.errored
