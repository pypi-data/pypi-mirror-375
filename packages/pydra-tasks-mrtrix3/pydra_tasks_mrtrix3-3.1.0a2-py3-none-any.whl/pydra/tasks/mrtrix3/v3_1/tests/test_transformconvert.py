# Auto-generated test for transformconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TransformConvert


@pytest.mark.xfail
def test_transformconvert(tmp_path, cli_parse_only):

    task = TransformConvert(
        debug=False,
        force=False,
        input=[File.sample()],
        operation="flirt_import",
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
