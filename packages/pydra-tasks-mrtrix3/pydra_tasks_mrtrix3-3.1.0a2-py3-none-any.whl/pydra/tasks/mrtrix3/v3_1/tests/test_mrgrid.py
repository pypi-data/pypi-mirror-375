# Auto-generated test for mrgrid

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrGrid


@pytest.mark.xfail
def test_mrgrid(tmp_path, cli_parse_only):

    task = MrGrid(
        all_axes=False,
        as_=None,
        axis=None,
        crop_unbound=False,
        datatype=None,
        debug=False,
        fill=None,
        force=False,
        in_file=Nifti1.sample(),
        interp=None,
        mask=None,
        operation="regrid",
        oversample=None,
        scale=None,
        size=None,
        strides=None,
        template=None,
        uniform=None,
        voxel=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
