# Auto-generated test for fivettgen_deep_atropos

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import FivettGen_Deep_atropos


@pytest.mark.xfail
def test_fivettgen_deep_atropos(tmp_path, cli_parse_only):

    task = FivettGen_Deep_atropos(
        cont=None,
        debug=False,
        force=False,
        in_file=Nifti1.sample(),
        nocleanup=False,
        nocrop=False,
        scratch=None,
        sgm_amyg_hipp=False,
        white_stem=False,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
