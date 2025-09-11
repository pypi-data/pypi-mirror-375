# Auto-generated test for fivettgen_fsl

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettGen_Fsl


@pytest.mark.xfail(reason="Job fivettgen_fsl is known not pass yet")
@pytest.mark.xfail
def test_fivettgen_fsl(tmp_path, cli_parse_only):

    task = FivettGen_Fsl(
        cont=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        mask=None,
        nocleanup=False,
        nocrop=False,
        premasked=False,
        scratch=None,
        sgm_amyg_hipp=False,
        t2=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
