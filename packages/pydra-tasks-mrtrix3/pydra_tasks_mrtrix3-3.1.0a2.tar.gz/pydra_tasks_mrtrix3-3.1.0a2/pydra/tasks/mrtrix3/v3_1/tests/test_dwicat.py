# Auto-generated test for dwicat

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiCat


@pytest.mark.xfail(reason="Job dwicat is known not pass yet")
@pytest.mark.xfail
def test_dwicat(tmp_path, cli_parse_only):

    task = DwiCat(
        cont=None,
        debug=False,
        force=False,
        inputs=Nifti1.sample(),
        mask=None,
        nocleanup=False,
        nointensity=False,
        scratch=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
