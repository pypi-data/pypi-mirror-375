# Auto-generated test for dwiextract

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiExtract


@pytest.mark.xfail
def test_dwiextract(tmp_path, cli_parse_only):

    task = DwiExtract(
        bzero=False,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        import_pe_eddy=None,
        import_pe_table=None,
        in_file=Nifti1.sample(),
        no_bzero=False,
        pe=None,
        shells=None,
        singleshell=False,
        strides=None,
        export_grad_fsl=None,
        export_grad_mrtrix=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
