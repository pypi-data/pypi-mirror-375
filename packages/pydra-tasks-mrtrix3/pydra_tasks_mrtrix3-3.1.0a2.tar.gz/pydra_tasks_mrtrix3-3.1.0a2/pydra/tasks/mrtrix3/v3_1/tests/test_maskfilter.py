# Auto-generated test for maskfilter

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MaskFilter


@pytest.mark.xfail
def test_maskfilter(tmp_path, cli_parse_only):

    task = MaskFilter(
        axes=None,
        connectivity=False,
        debug=False,
        extent=None,
        filter="clean",
        force=False,
        in_file=Nifti1.sample(),
        largest=False,
        minsize=None,
        npass=None,
        scale=None,
        strides=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
