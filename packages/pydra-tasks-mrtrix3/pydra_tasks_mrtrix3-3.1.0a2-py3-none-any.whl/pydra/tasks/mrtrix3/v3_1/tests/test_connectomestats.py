# Auto-generated test for connectomestats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import ConnectomeStats


@pytest.mark.xfail
def test_connectomestats(tmp_path, cli_parse_only):

    task = ConnectomeStats(
        algorithm="nbs",
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
        nonstationarity=False,
        notest=False,
        nshuffles=None,
        nshuffles_nonstationarity=None,
        output="a-string",
        permutations=None,
        permutations_nonstationarity=None,
        skew_nonstationarity=None,
        strong=False,
        tfce_dh=None,
        tfce_e=None,
        tfce_h=None,
        threshold=None,
        variance=None,
    )
    result = task(worker="debug")
    assert not result.errored
