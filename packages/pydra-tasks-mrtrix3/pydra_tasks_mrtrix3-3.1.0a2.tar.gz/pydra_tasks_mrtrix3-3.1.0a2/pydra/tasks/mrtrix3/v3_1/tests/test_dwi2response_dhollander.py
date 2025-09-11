# Auto-generated test for dwi2response_dhollander

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Response_Dhollander


@pytest.mark.xfail(reason="Job dwi2response_dhollander is known not pass yet")
@pytest.mark.xfail
def test_dwi2response_dhollander(tmp_path, cli_parse_only):

    task = Dwi2Response_Dhollander(
        cont=None,
        csf=None,
        debug=False,
        erode=None,
        fa=None,
        force=False,
        fslgrad=None,
        gm=None,
        grad=None,
        in_file=Nifti1.sample(),
        lmax=None,
        mask=None,
        nocleanup=False,
        scratch=None,
        sfwm=None,
        shells=None,
        wm_algo=None,
        out_csf=File.sample(),
        out_gm=File.sample(),
        out_sfwm=File.sample(),
        voxels=None,
    )
    result = task(worker="debug")
    assert not result.errored
