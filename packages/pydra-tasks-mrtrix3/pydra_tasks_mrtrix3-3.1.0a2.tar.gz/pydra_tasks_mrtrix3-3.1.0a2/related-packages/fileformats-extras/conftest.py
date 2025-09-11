import os
import logging
from pathlib import Path
import tempfile
import typing as ty
import pytest
from fileformats.medimage import DicomDir, Nifti

# Set DEBUG logging for unittests

log_level = logging.WARNING

logger = logging.getLogger("fileformats")
logger.setLevel(log_level)

sch = logging.StreamHandler()
sch.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sch.setFormatter(formatter)
logger.addHandler(sch)


# For debugging in IDE's don't catch raised exceptions and let the IDE
# break at it
if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[ty.Any]) -> None:
        if call.excinfo is not None:
            raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[BaseException]) -> None:
        raise excinfo.value


@pytest.fixture
def work_dir():
    work_dir = tempfile.mkdtemp()
    return Path(work_dir)


@pytest.fixture(scope="session")
def dummy_dwi_dicom():
    import medimages4tests.dummy.dicom.mri.dwi.siemens.skyra.syngo_d13c as module

    return DicomDir(module.get_image())


@pytest.fixture(scope="session")
def dummy_nifti():
    import medimages4tests.dummy.nifti as module

    return Nifti(module.get_image())
