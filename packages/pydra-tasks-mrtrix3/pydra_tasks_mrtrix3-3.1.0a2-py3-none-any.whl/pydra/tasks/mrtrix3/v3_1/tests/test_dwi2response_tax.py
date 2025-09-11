# Auto-generated test for dwi2response_tax

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Response_Tax


@pytest.mark.xfail(reason="Job dwi2response_tax is known not pass yet")
@pytest.mark.xfail
def test_dwi2response_tax(tmp_path, cli_parse_only):

    task = Dwi2Response_Tax(
        cont=None,
        convergence=None,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        lmax=None,
        mask=None,
        max_iters=None,
        nocleanup=False,
        peak_ratio=None,
        scratch=None,
        shells=None,
        out_file=File.sample(),
        voxels=None,
    )
    result = task(worker="debug")
    assert not result.errored
