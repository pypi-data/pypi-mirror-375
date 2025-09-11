# Auto-generated test for mrdegibbs

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrDegibbs


@pytest.mark.xfail
def test_mrdegibbs(tmp_path, cli_parse_only):

    task = MrDegibbs(
        axes=None,
        datatype=None,
        debug=False,
        force=False,
        in_=Nifti1.sample(),
        maxW=None,
        minW=None,
        mode=None,
        nshifts=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
