# Auto-generated test for mrtransform

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrTransform


@pytest.mark.xfail(reason="Job mrtransform is known not pass yet")
@pytest.mark.xfail
def test_mrtransform(tmp_path, cli_parse_only):

    task = MrTransform(
        datatype=None,
        debug=False,
        directions=None,
        flip=None,
        force=False,
        from_=None,
        fslgrad=None,
        grad=None,
        half=False,
        identity=False,
        in_file=Nifti1.sample(),
        interp=None,
        inverse=False,
        linear=None,
        midway_space=False,
        modulate=None,
        nan=False,
        no_reorientation=False,
        oversample=None,
        reorient_fod=False,
        replace=None,
        strides=None,
        template=None,
        warp=None,
        warp_full=None,
        export_grad_fsl=None,
        export_grad_mrtrix=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
