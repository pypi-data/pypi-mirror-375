# Auto-generated test for tckglobal

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckGlobal


@pytest.mark.xfail
def test_tckglobal(tmp_path, cli_parse_only):

    task = TckGlobal(
        balance=None,
        beta=None,
        cpot=None,
        debug=False,
        density=None,
        force=False,
        grad=None,
        lambda_=None,
        length=None,
        lmax=None,
        mask=None,
        niter=None,
        noapo=False,
        ppot=None,
        prob=None,
        response=File.sample(),
        riso=None,
        source=Nifti1.sample(),
        t0=None,
        t1=None,
        tracks=Tracks.sample(),
        weight=None,
        eext=None,
        etrend=None,
        fiso=None,
        fod=None,
    )
    result = task(worker="debug")
    assert not result.errored
