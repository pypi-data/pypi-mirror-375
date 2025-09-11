# Auto-generated test for dwi2response_msmt_5tt

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Response_Msmt_5tt


@pytest.mark.xfail(reason="Job dwi2response_msmt_5tt is known not pass yet")
@pytest.mark.xfail
def test_dwi2response_msmt_5tt(tmp_path, cli_parse_only):

    task = Dwi2Response_Msmt_5tt(
        cont=None,
        debug=False,
        dirs=None,
        fa=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_5tt=Nifti1.sample(),
        in_file=Nifti1.sample(),
        lmax=None,
        mask=None,
        nocleanup=False,
        pvf=None,
        scratch=None,
        sfwm_fa_threshold=None,
        shells=None,
        wm_algo=None,
        out_csf=File.sample(),
        out_gm=File.sample(),
        out_wm=File.sample(),
        voxels=None,
    )
    result = task(worker="debug")
    assert not result.errored
