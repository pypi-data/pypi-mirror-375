# Auto-generated test for amp2response

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Amp2Response


@pytest.mark.xfail
def test_amp2response(tmp_path, cli_parse_only):

    task = Amp2Response(
        amps=Nifti1.sample(),
        debug=False,
        directions=None,
        directions_image=Nifti1.sample(),
        force=False,
        isotropic=False,
        lmax=None,
        mask=Nifti1.sample(),
        noconstraint=False,
        shells=None,
        response=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
