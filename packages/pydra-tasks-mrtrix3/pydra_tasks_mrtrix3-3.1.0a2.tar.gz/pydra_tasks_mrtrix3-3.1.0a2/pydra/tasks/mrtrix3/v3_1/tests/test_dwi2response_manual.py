# Auto-generated test for dwi2response_manual

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Response_Manual


@pytest.mark.xfail(reason="Job dwi2response_manual is known not pass yet")
@pytest.mark.xfail
def test_dwi2response_manual(tmp_path, cli_parse_only):

    task = Dwi2Response_Manual(
        cont=None,
        debug=False,
        dirs=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        in_voxels=Nifti1.sample(),
        lmax=None,
        mask=None,
        nocleanup=False,
        scratch=None,
        shells=None,
        out_file=File.sample(),
        voxels=None,
    )
    result = task(worker="debug")
    assert not result.errored
