# Auto-generated test for dwi2mask_synthstrip

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Mask_Synthstrip


@pytest.mark.xfail(reason="Job dwi2mask_synthstrip is known not pass yet")
@pytest.mark.xfail
def test_dwi2mask_synthstrip(tmp_path, cli_parse_only):

    task = Dwi2Mask_Synthstrip(
        border=None,
        cont=None,
        debug=False,
        force=False,
        fslgrad=None,
        gpu=False,
        grad=None,
        in_file=Nifti1.sample(),
        model=None,
        nocleanup=False,
        nocsf=False,
        scratch=None,
        out_file=File.sample(),
        stripped=None,
    )
    result = task(worker="debug")
    assert not result.errored
