# Auto-generated test for responsemean

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import ResponseMean


@pytest.mark.xfail(reason="Job responsemean is known not pass yet")
@pytest.mark.xfail
def test_responsemean(tmp_path, cli_parse_only):

    task = ResponseMean(
        cont=None,
        debug=False,
        force=False,
        inputs=File.sample(),
        legacy=False,
        nocleanup=False,
        scratch=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
