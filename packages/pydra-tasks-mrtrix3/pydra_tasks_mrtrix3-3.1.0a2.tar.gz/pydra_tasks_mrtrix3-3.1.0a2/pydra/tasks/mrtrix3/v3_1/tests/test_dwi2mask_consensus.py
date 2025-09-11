# Auto-generated test for dwi2mask_consensus

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Dwi2Mask_Consensus


@pytest.mark.xfail(reason="Job dwi2mask_consensus is known not pass yet")
@pytest.mark.xfail
def test_dwi2mask_consensus(tmp_path, cli_parse_only):

    task = Dwi2Mask_Consensus(
        algorithms=None,
        cont=None,
        debug=False,
        force=False,
        fslgrad=None,
        grad=None,
        in_file=Nifti1.sample(),
        nocleanup=False,
        scratch=None,
        template=None,
        threshold=None,
        masks=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
