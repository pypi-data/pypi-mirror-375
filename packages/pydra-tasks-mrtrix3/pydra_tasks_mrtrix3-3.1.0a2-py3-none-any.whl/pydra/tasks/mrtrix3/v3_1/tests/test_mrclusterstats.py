# Auto-generated test for mrclusterstats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrClusterstats


@pytest.mark.xfail
def test_mrclusterstats(tmp_path, cli_parse_only):

    task = MrClusterstats(
        column=None,
        connectivity=False,
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
        mask=Nifti1.sample(),
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
