# Auto-generated test for tckgen

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import TckGen


@pytest.mark.xfail
def test_tckgen(tmp_path, cli_parse_only):

    task = TckGen(
        act=None,
        algorithm=None,
        angle=None,
        backtrack=False,
        crop_at_gmwmi=False,
        cutoff=None,
        debug=False,
        downsample=None,
        exclude=None,
        force=False,
        fslgrad=None,
        grad=None,
        include=None,
        include_ordered=None,
        mask=None,
        max_attempts_per_seed=None,
        maxlength=None,
        minlength=None,
        noprecomputed=False,
        power=None,
        rk4=False,
        samples=None,
        seed_cutoff=None,
        seed_direction=None,
        seed_dynamic=None,
        seed_gmwmi=None,
        seed_grid_per_voxel=None,
        seed_image=None,
        seed_random_per_voxel=None,
        seed_rejection=None,
        seed_sphere=None,
        seed_unidirectional=False,
        seeds=None,
        select=None,
        source=Nifti1.sample(),
        step=None,
        stop=False,
        tracks=Tracks.sample(),
        trials=None,
        output_seeds=None,
    )
    result = task(worker="debug")
    assert not result.errored
