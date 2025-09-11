# Auto-generated test for tckdfc

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckDfc


@pytest.mark.xfail
def test_tckdfc(tmp_path, cli_parse_only):

    task = TckDfc(
        backtrack=False,
        debug=False,
        dynamic=None,
        fmri=Nifti1.sample(),
        force=False,
        stat_vox=None,
        static=False,
        template=None,
        tracks=File.sample(),
        upsample=None,
        vox=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
