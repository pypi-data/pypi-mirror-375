# Auto-generated test for tcksift2

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckSift2


@pytest.mark.xfail
def test_tcksift2(tmp_path, cli_parse_only):

    task = TckSift2(
        act=None,
        debug=False,
        fd_scale_gm=False,
        fd_thresh=None,
        force=False,
        in_fod=Nifti1.sample(),
        in_tracks=Tracks.sample(),
        linear=False,
        make_null_lobes=False,
        max_coeff=None,
        max_coeff_step=None,
        max_factor=None,
        max_iters=None,
        min_cf_decrease=None,
        min_coeff=None,
        min_factor=None,
        min_iters=None,
        min_td_frac=None,
        no_dilate_lut=False,
        proc_mask=None,
        reg_tikhonov=None,
        reg_tv=None,
        remove_untracked=False,
        csv=None,
        out_coeffs=None,
        out_mu=None,
        out_weights=File.sample(),
        output_debug=None,
    )
    result = task(worker="debug")
    assert not result.errored
