import typing  # noqa: F401
import numpy.typing
from fileformats.core import extra_implementation
from fileformats.medimage import DwiEncoding
from fileformats.medimage.diffusion import EncodingArrayType
from fileformats.medimage_mrtrix3 import BFile


@extra_implementation(DwiEncoding.read_array)
def bfile_read_array(
    bfile: BFile,
) -> EncodingArrayType:
    return numpy.asarray(
        [[float(x) for x in ln.split()] for ln in bfile.read_contents().splitlines()]
    )
