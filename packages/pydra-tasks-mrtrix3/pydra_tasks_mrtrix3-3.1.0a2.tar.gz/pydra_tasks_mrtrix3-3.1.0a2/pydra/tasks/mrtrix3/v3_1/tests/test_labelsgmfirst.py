# Auto-generated test for labelsgmfirst

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import LabelSgmfirst


@pytest.mark.xfail
def test_labelsgmfirst(tmp_path, cli_parse_only):

    task = LabelSgmfirst(
        cont=None,
        debug=False,
        force=False,
        lut=File.sample(),
        nocleanup=False,
        parc=Nifti1.sample(),
        premasked=False,
        scratch=None,
        sgm_amyg_hipp=False,
        t1=Nifti1.sample(),
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
