# Auto-generated test for fixelcfestats

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FixelCfestats


@pytest.mark.xfail(reason="Job fixelcfestats is known not pass yet")
@pytest.mark.xfail
def test_fixelcfestats(tmp_path, cli_parse_only):

    task = FixelCfestats(
        cfe_c=None,
        cfe_dh=None,
        cfe_e=None,
        cfe_h=None,
        cfe_legacy=False,
        column=None,
        connectivity=File.sample(),
        contrast=File.sample(),
        debug=False,
        design=File.sample(),
        errors=None,
        exchange_whole=None,
        exchange_within=None,
        fonly=False,
        force=False,
        ftests=None,
        in_fixel_directory=File.sample(),
        mask=None,
        nonstationarity=False,
        notest=False,
        nshuffles=None,
        nshuffles_nonstationarity=None,
        out_fixel_directory="a-string",
        permutations=None,
        permutations_nonstationarity=None,
        skew_nonstationarity=None,
        strong=False,
        subjects=Nifti1.sample(),
        variance=None,
    )
    result = task(worker="debug")
    assert not result.errored
