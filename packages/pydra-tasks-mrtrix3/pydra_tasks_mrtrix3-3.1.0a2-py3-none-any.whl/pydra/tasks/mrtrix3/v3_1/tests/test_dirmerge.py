# Auto-generated test for dirmerge

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import DirMerge


@pytest.mark.xfail
def test_dirmerge(tmp_path, cli_parse_only):

    task = DirMerge(
        bvalue_files=["a-string"],
        debug=False,
        firstisfirst=False,
        force=False,
        subsets=1,
        unipolar_weight=None,
        out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
