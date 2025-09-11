# Auto-generated test for mtnormalise

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MtNormalise


@pytest.mark.xfail
def test_mtnormalise(tmp_path, cli_parse_only):

    task = MtNormalise(
        balanced=False,
        debug=False,
        force=False,
        input_output=[File.sample()],
        mask=Nifti1.sample(),
        niter=None,
        order=None,
        reference=None,
        check_factors=None,
        check_mask=None,
        check_norm=None,
    )
    result = task(worker="debug")
    assert not result.errored
