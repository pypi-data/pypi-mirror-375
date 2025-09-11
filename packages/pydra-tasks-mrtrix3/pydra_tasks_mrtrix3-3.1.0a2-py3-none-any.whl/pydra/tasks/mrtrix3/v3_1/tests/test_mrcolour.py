# Auto-generated test for mrcolour

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrColour


@pytest.mark.xfail
def test_mrcolour(tmp_path, cli_parse_only):

    task = MrColour(
        colour=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        lower=None,
        map="gray",
        upper=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
