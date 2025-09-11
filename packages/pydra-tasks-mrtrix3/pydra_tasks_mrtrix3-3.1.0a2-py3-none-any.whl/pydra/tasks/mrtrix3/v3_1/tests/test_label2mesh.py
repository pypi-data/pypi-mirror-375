# Auto-generated test for label2mesh

import pytest
from fileformats.generic import File, Directory, FsObject  # noqa
from fileformats.medimage import Nifti1  # noqa
from fileformats.medimage_mrtrix3 import ImageFormat, ImageIn, Tracks  # noqa
from pydra.tasks.mrtrix3.v3_1 import Label2Mesh


@pytest.mark.xfail
def test_label2mesh(tmp_path, cli_parse_only):

    task = Label2Mesh(
        blocky=False,
        debug=False,
        force=False,
        nodes_in=Nifti1.sample(),
        mesh_out=File.sample(),
    )
    result = task(worker="debug")
    assert not result.errored
