# Auto-generated test for mrinfo

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrInfo


@pytest.mark.xfail
def test_mrinfo(tmp_path, cli_parse_only):

    task = MrInfo(
        all=False,
        bvalue_scaling=False,
        datatype=False,
        debug=False,
        dwgrad=False,
        force=False,
        format=False,
        fslgrad=None,
        grad=None,
        image_=[Nifti1.sample()],
        multiplier=False,
        name=False,
        ndim=False,
        nodelete=False,
        offset=False,
        petable=False,
        property=None,
        shell_bvalues=False,
        shell_indices=False,
        shell_sizes=False,
        size=False,
        spacing=False,
        strides=False,
        transform=False,
        export_grad_fsl=None,
        export_grad_mrtrix=None,
        export_pe_eddy=None,
        export_pe_table=None,
        json_all=None,
        json_keyval=None,
    )
    result = task(worker="debug")
    assert not result.errored
