# Auto-generated test for fixelcorrespondence

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FixelCorrespondence


@pytest.mark.xfail(reason="Job fixelcorrespondence is known not pass yet")
@pytest.mark.xfail
def test_fixelcorrespondence(tmp_path, cli_parse_only):

    task = FixelCorrespondence(
        angle=None,
        debug=False,
        force=False,
        output_data="a-string",
        output_directory="a-string",
        subject_data=Nifti1.sample(),
        template_directory=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
