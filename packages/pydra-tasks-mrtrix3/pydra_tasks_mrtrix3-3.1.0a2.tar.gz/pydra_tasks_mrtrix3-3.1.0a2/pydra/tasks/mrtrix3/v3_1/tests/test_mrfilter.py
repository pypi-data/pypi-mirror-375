# Auto-generated test for mrfilter

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrFilter


@pytest.mark.xfail
def test_mrfilter(tmp_path, cli_parse_only):

    task = MrFilter(
        axes=None,
        bridge=None,
        centre_zero=False,
        debug=False,
        extent=None,
        filter="fft",
        force=False,
        fwhm=None,
        in_file=Nifti1.sample(),
        inverse=False,
        magnitude=False,
        maskin=None,
        rescale=False,
        scanner=False,
        stdev=None,
        strides=None,
        zlower=None,
        zupper=None,
        maskout=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
