# Auto-generated test for dwibiascorrect_fsl

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiBiascorrect_Fsl


@pytest.mark.xfail(reason="Job dwibiascorrect_fsl is known not pass yet")
@pytest.mark.xfail
def test_dwibiascorrect_fsl(tmp_path, cli_parse_only):

    task = DwiBiascorrect_Fsl(
        cont=None,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        mask=None,
        nocleanup=False,
        scratch=None,
        bias=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
