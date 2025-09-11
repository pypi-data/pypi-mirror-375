# Auto-generated test for vectorstats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import VectorStats


@pytest.mark.xfail
def test_vectorstats(tmp_path, cli_parse_only):

    task = VectorStats(
        column=None,
        contrast=File.sample(),
        debug=False,
        design=File.sample(),
        errors=None,
        exchange_whole=None,
        exchange_within=None,
        fonly=False,
        force=False,
        ftests=None,
        in_file=File.sample(),
        notest=False,
        nshuffles=None,
        output="a-string",
        permutations=None,
        strong=False,
        variance=None,
    )
    result = task(worker="debug")
    assert not result.errored
