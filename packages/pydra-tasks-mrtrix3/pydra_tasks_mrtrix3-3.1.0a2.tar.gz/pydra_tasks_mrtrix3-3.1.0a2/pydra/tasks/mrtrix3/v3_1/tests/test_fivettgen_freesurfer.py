# Auto-generated test for fivettgen_freesurfer

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettGen_Freesurfer


@pytest.mark.xfail(reason="Job fivettgen_freesurfer is known not pass yet")
@pytest.mark.xfail
def test_fivettgen_freesurfer(tmp_path, cli_parse_only):

    task = FivettGen_Freesurfer(
        cont=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        lut=None,
        nocleanup=False,
        nocrop=False,
        scratch=None,
        sgm_amyg_hipp=False,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
