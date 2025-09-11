# Auto-generated test for dwinormalise_group

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiNormalise_Group


@pytest.mark.xfail(reason="Job dwinormalise_group is known not pass yet")
@pytest.mark.xfail
def test_dwinormalise_group(tmp_path, cli_parse_only):

    task = DwiNormalise_Group(
        cont=None,
        debug=False,
        fa_threshold=None,
        force=False,
        input_dir=File.sample(),
        mask_dir=File.sample(),
        nocleanup=False,
        scratch=None,
        fa_template=File.sample(),
        output_dir=File.sample(),
        wm_mask=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
