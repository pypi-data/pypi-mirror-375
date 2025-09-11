import typing as ty
from fileformats.core import converter, FileSet
from fileformats.medimage.base import MedicalImage
from fileformats.medimage_mrtrix3 import (
    ImageFormat as MrtrixImage,
    ImageHeader as MrtrixImageHeader,
    ImageFormatGz as MrtrixImageGz,
)

from pydra.tasks.mrtrix3.v3_0 import MrConvert


def out_file_template(fileformat: ty.Type[FileSet]) -> str:
    """Return the output file name for a given file format

    Parameters
    ----------
    fileformat : type
        the file format class

    Returns
    -------
    str
        the output file name
    """
    return "out" + fileformat.ext


# Register MrConvert as a converter for MrTrix formats

converter(
    source_format=MedicalImage,
    target_format=MrtrixImageGz,
    out_file=out_file_template(MrtrixImageGz),
)(MrConvert)

converter(
    source_format=MedicalImage,
    target_format=MrtrixImageHeader,
    out_file=out_file_template(MrtrixImageHeader),
)(MrConvert)

converter(
    source_format=MedicalImage,
    target_format=MrtrixImage,
    out_file=out_file_template(MrtrixImage),
)(MrConvert)
