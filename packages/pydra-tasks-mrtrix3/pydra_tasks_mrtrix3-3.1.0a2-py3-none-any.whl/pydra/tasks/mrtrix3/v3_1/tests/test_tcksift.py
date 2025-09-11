# Auto-generated test for tcksift

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckSift


@pytest.mark.xfail
def test_tcksift(tmp_path, cli_parse_only):

    task = TckSift(
        act=None,
        debug=False,
        fd_scale_gm=False,
        fd_thresh=None,
        force=False,
        in_fod=Nifti1.sample(),
        in_tracks=Tracks.sample(),
        make_null_lobes=False,
        no_dilate_lut=False,
        nofilter=False,
        out_tracks=Tracks.sample(),
        output_at_counts=None,
        proc_mask=None,
        remove_untracked=False,
        term_mu=None,
        term_number=None,
        term_ratio=None,
        csv=None,
        out_mu=None,
        out_selection=None,
        output_debug=None,
    )
    result = task(worker="debug")
    assert not result.errored
