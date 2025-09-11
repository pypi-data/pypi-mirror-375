# Auto-generated test for dwi2mask_b02template

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Mask_B02template


@pytest.mark.xfail(reason="Job dwi2mask_b02template is known not pass yet")
@pytest.mark.xfail
def test_dwi2mask_b02template(tmp_path, cli_parse_only):

    task = Dwi2Mask_B02template(
        ants_options=None,
        cont=None,
        debug=False,
        flirt_options=None,
        fnirt_config=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        nocleanup=False,
        scratch=None,
        software=None,
        template=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
