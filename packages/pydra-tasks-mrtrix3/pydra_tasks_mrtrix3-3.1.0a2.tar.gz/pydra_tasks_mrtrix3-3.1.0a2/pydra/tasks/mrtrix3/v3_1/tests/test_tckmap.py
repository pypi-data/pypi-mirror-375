# Auto-generated test for tckmap

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckMap


@pytest.mark.xfail
def test_tckmap(tmp_path, cli_parse_only):

    task = TckMap(
        backtrack=False,
        contrast=None,
        datatype=None,
        debug=False,
        dec=False,
        dixel=None,
        ends_only=False,
        force=False,
        fwhm_tck=None,
        image_=None,
        map_zero=False,
        precise=False,
        stat_tck=None,
        stat_vox=None,
        tck_weights_in=None,
        template=None,
        tod=None,
        tracks=File.sample(),
        upsample=None,
        vector_file=None,
        vox=None,
        out_file=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
