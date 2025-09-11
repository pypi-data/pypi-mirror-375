# Auto-generated test for fivettedit

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettEdit


@pytest.mark.xfail
def test_fivettedit(tmp_path, cli_parse_only):

    task = FivettEdit(
        cgm=None,
        csf=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        none=None,
        path=None,
        sgm=None,
        wm=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
