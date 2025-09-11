# Auto-generated test for mredit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrEdit


@pytest.mark.xfail
def test_mredit(tmp_path, cli_parse_only):

    task = MrEdit(
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        plane=None,
        scanner=False,
        sphere=None,
        voxel=None,
        out_file=None,
    )
    result = task(worker="debug")
    assert not result.errored
