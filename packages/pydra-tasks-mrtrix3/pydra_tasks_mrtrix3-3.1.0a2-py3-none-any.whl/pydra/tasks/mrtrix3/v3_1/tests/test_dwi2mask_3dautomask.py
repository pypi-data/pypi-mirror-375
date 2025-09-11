# Auto-generated test for dwi2mask_3dautomask

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Mask_3dautomask


@pytest.mark.xfail(reason="Job dwi2mask_3dautomask is known not pass yet")
@pytest.mark.xfail
def test_dwi2mask_3dautomask(tmp_path, cli_parse_only):

    task = Dwi2Mask_3dautomask(
        NN1=False,
        NN2=False,
        NN3=False,
        SI=None,
        clfrac=None,
        cont=None,
        debug=False,
        dilate=None,
        eclip=False,
        erode=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        nbhrs=None,
        nocleanup=False,
        nograd=False,
        peels=None,
        scratch=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
