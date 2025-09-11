# Auto-generated test for transformcompose

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TransformCompose


@pytest.mark.xfail
def test_transformcompose(tmp_path, cli_parse_only):

    task = TransformCompose(
        debug=False,
        force=False,
        in_file=[File.sample()],
        output=File.sample(),
        template=None,
    )
    result = task(worker="debug")
    assert not result.errored
