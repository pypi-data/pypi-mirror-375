# Auto-generated test for mrconvert

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrConvert


@pytest.mark.xfail(reason="Job mrconvert is known not pass yet")
@pytest.mark.xfail
def test_mrconvert(tmp_path, cli_parse_only):

    task = MrConvert(
        append_property=None,
        axes=None,
        bvalue_scaling=False,
        clear_property=None,
        coord=None,
        copy_properties=None,
        datatype=None,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        import_pe_eddy=None,
        import_pe_table=None,
        in_file=Nifti1.sample(),
        json_import=None,
        scaling=None,
        set_property=None,
        strides=None,
        vox=None,
        export_grad_fsl=None,
        export_grad_mrtrix=None,
        export_pe_eddy=None,
        export_pe_table=None,
        json_export=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
