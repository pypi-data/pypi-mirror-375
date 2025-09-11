# Auto-generated test for mask2glass

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Mask2Glass


@pytest.mark.xfail(reason="Job mask2glass is known not pass yet")
@pytest.mark.xfail
def test_mask2glass(tmp_path, cli_parse_only):

    task = Mask2Glass(
        cont=None,
        debug=False,
        dilate=None,
        force=False,
        in_file=Nifti1.sample(),
        nocleanup=False,
        scale=None,
        scratch=None,
        smooth=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
