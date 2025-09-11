# Auto-generated test for dwi2mask_mtnorm

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Mask_Mtnorm


@pytest.mark.xfail(reason="Job dwi2mask_mtnorm is known not pass yet")
@pytest.mark.xfail
def test_dwi2mask_mtnorm(tmp_path, cli_parse_only):

    task = Dwi2Mask_Mtnorm(
        cont=None,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        init_mask=None,
        lmax=None,
        nocleanup=False,
        scratch=None,
        threshold=None,
        out_file=File.sample(),
        tissuesum=None,
    )
    result = task(worker="debug")
    assert not result.errored
