# Auto-generated test for fixel2sh

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fixel2Sh


@pytest.mark.xfail
def test_fixel2sh(tmp_path, cli_parse_only):

    task = Fixel2Sh(
        debug=False,
        fixel_in=Nifti1.sample(),
        force=False,
        lmax=None,
        sh_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
