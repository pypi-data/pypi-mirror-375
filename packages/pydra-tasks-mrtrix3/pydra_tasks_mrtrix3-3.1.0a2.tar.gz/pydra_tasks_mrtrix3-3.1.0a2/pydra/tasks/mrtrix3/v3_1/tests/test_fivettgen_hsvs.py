# Auto-generated test for fivettgen_hsvs

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettGen_Hsvs


@pytest.mark.xfail(reason="Job fivettgen_hsvs is known not pass yet")
@pytest.mark.xfail
def test_fivettgen_hsvs(tmp_path, cli_parse_only):

    task = FivettGen_Hsvs(
        cont=None,
        debug=False,
        force=False,
        freesurfer_lut=None,
        hippocampi=None,
        in_file=File.sample(),
        nocleanup=False,
        nocrop=False,
        scratch=None,
        sgm_amyg_hipp=False,
        template=None,
        thalami=None,
        white_stem=False,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
