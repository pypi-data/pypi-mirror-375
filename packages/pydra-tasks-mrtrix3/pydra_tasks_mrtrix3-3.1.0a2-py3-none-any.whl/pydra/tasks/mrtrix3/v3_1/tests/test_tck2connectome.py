# Auto-generated test for tck2connectome

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Tck2Connectome


@pytest.mark.xfail
def test_tck2connectome(tmp_path, cli_parse_only):

    task = Tck2Connectome(
        assignment_all_voxels=False,
        assignment_end_voxels=False,
        assignment_forward_search=None,
        assignment_radial_search=None,
        assignment_reverse_search=None,
        debug=False,
        force=False,
        keep_unassigned=False,
        nodes_in=Nifti1.sample(),
        scale_file=None,
        scale_invlength=False,
        scale_invnodevol=False,
        scale_length=False,
        stat_edge=None,
        symmetric=False,
        tck_weights_in=None,
        tracks_in=Tracks.sample(),
        vector=False,
        zero_diagonal=False,
        connectome_out=File.sample(),
        out_assignments=None,
    )
    result = task(worker="debug")
    assert not result.errored
