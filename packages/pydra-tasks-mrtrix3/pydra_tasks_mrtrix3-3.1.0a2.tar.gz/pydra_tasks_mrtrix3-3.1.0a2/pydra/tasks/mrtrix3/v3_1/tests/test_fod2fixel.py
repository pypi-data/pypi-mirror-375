# Auto-generated test for fod2fixel

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Fod2Fixel


@pytest.mark.xfail
def test_fod2fixel(tmp_path, cli_parse_only):

    task = Fod2Fixel(
        debug=False,
        dirpeak=False,
        fmls_integral=None,
        fmls_lobe_merge_ratio=None,
        fmls_no_thresholds=False,
        fmls_peak_value=None,
        fod=Nifti1.sample(),
        force=False,
        mask=None,
        maxnum=None,
        nii=False,
        afd=None,
        disp=None,
        fixel_directory=File.sample(),
        peak_amp=None,
    )
    result = task(worker="debug")
    assert not result.errored
