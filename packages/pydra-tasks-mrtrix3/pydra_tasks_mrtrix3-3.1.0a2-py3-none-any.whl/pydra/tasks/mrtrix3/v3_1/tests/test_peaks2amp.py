# Auto-generated test for peaks2amp

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Peaks2Amp


@pytest.mark.xfail
def test_peaks2amp(tmp_path, cli_parse_only):

    task = Peaks2Amp(
        debug=False,
        directions=Nifti1.sample(),
        force=False,
        amplitudes=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
