# Auto-generated test for mrregister

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import MrRegister


@pytest.mark.xfail
def test_mrregister(tmp_path, cli_parse_only):

    task = MrRegister(
        affine_init_matrix=None,
        affine_init_rotation=None,
        affine_init_translation=None,
        affine_lmax=None,
        affine_metric=None,
        affine_metric_diff_estimator=None,
        affine_niter=None,
        affine_scale=None,
        contrast1_contrast2=None,
        datatype=None,
        debug=False,
        diagnostics_image=None,
        directions=None,
        force=False,
        image1_image2=Nifti1.sample(),
        init_rotation_search_angles=None,
        init_rotation_search_directions=None,
        init_rotation_search_global_iterations=None,
        init_rotation_search_run_global=False,
        init_rotation_search_scale=None,
        init_rotation_unmasked1=False,
        init_rotation_unmasked2=False,
        init_translation_unmasked1=False,
        init_translation_unmasked2=False,
        linstage_diagnostics_prefix=None,
        linstage_iterations=None,
        linstage_optimiser_default=None,
        linstage_optimiser_first=None,
        linstage_optimiser_last=None,
        mask1=None,
        mask2=None,
        mc_weights=None,
        nan=False,
        nl_disp_smooth=None,
        nl_grad_step=None,
        nl_init=None,
        nl_lmax=None,
        nl_niter=None,
        nl_scale=None,
        nl_update_smooth=None,
        noreorientation=False,
        rigid_init_matrix=None,
        rigid_init_rotation=None,
        rigid_init_translation=None,
        rigid_lmax=None,
        rigid_metric=None,
        rigid_metric_diff_estimator=None,
        rigid_niter=None,
        rigid_scale=None,
        type=None,
        affine=None,
        affine_1tomidway=None,
        affine_2tomidway=None,
        affine_log=None,
        nl_warp=None,
        nl_warp_full=None,
        rigid=None,
        rigid_1tomidway=None,
        rigid_2tomidway=None,
        rigid_log=None,
        transformed=None,
        transformed_midway=None,
    )
    result = task(worker="debug")
    assert not result.errored
