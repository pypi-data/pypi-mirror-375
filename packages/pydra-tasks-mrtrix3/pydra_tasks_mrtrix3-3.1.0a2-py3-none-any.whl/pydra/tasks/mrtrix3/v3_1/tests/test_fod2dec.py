# Auto-generated test for fod2dec

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fod2Dec


@pytest.mark.xfail
def test_fod2dec(tmp_path, cli_parse_only):

    task = Fod2Dec(
        contrast=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        lum=False,
        lum_coefs=None,
        lum_gamma=None,
        mask=None,
        no_weight=False,
        threshold=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
