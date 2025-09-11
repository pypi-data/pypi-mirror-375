# Auto-generated test for mrmath

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrMath


@pytest.mark.xfail
def test_mrmath(tmp_path, cli_parse_only):

    task = MrMath(
        axis=None,
        datatype=None,
        debug=False,
        force=False,
        in_file=[Nifti1.sample()],
        keep_unary_axes=False,
        operation="mean",
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
