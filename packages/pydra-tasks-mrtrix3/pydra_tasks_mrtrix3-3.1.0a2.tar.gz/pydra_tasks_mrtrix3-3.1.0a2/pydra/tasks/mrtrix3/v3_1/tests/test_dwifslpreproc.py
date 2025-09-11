# Auto-generated test for dwifslpreproc

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DwiFslpreproc


@pytest.mark.xfail(reason="Job dwifslpreproc is known not pass yet")
@pytest.mark.xfail
def test_dwifslpreproc(tmp_path, cli_parse_only):

    task = DwiFslpreproc(
        align_seepi=False,
        cont=None,
        debug=False,
        eddy_mask=None,
        eddy_options=None,
        eddy_slspec=None,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        json_import=None,
        nocleanup=False,
        pe_dir=None,
        readout_time=None,
        rpe_all=False,
        rpe_header=False,
        rpe_none=False,
        rpe_pair=False,
        scratch=None,
        se_epi=None,
        topup_files=None,
        topup_options=None,
        eddyqc_all=None,
        eddyqc_text=None,
        export_grad_fsl=None,
        export_grad_mrtrix=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
