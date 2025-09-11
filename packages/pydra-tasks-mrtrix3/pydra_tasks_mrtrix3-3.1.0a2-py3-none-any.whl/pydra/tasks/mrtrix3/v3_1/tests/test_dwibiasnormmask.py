# Auto-generated test for dwibiasnormmask

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiBiasnormmask


@pytest.mark.xfail(reason="Job dwibiasnormmask is known not pass yet")
@pytest.mark.xfail
def test_dwibiasnormmask(tmp_path, cli_parse_only):

    task = DwiBiasnormmask(
        cont=None,
        debug=False,
        dice=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        init_mask=None,
        lmax=None,
        mask_algo=None,
        max_iters=None,
        nocleanup=False,
        reference=None,
        scratch=None,
        output_bias=None,
        output_dwi=File.sample(),
        output_mask=File.sample(),
        output_scale=None,
        output_tissuesum=None,
    )
    result = task(worker="debug")
    assert not result.errored
