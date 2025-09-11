# Auto-generated test for population_template

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import PopulationTemplate


@pytest.mark.xfail(reason="Job population_template is known not pass yet")
@pytest.mark.xfail
def test_population_template(tmp_path, cli_parse_only):

    task = PopulationTemplate(
        affine_lmax=None,
        affine_niter=None,
        affine_scale=None,
        aggregate=None,
        aggregation_weights=None,
        cont=None,
        copy_input=False,
        debug=False,
        delete_temporary_files=False,
        force=False,
        initial_alignment=None,
        input_dir=File.sample(),
        leave_one_out=None,
        linear_estimator=None,
        linear_no_drift_correction=False,
        linear_no_pause=False,
        mask_dir=None,
        mc_weight_affine=None,
        mc_weight_initial_alignment=None,
        mc_weight_nl=None,
        mc_weight_rigid=None,
        nanmask=False,
        nl_disp_smooth=None,
        nl_grad_step=None,
        nl_lmax=None,
        nl_niter=None,
        nl_scale=None,
        nl_update_smooth=None,
        nocleanup=False,
        noreorientation=False,
        rigid_lmax=None,
        rigid_niter=None,
        rigid_scale=None,
        scratch=None,
        type=None,
        voxel_size=None,
        linear_transformations_dir=None,
        template=File.sample(),
        template_mask=None,
        transformed_dir=None,
        warp_dir=None,
    )
    result = task(worker="debug")
    assert not result.errored
