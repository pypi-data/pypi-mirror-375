import os
import sys
from unittest import mock
import typing as ty
from pathlib import Path
import numpy as np
import numpy.typing
from medimages4tests.dummy.nifti import get_image as get_dummy_nifti
from fileformats.core import FileSet, SampleFileGenerator, extra_implementation
from fileformats.medimage import MedicalImage, Nifti1
from fileformats.medimage_mrtrix3 import ImageFormat

# if sys.version_info >= (3, 9):
#     from typing import TypeAlias
# else:
#     from typing_extensions import TypeAlias


# DataArrayType: TypeAlias = (
#     "numpy.typing.NDArray[ty.Union[np.floating[ty.Any], np.integer[ty.Any]]]"
# )


@extra_implementation(FileSet.generate_sample_data)
def generate_mrtrix_sample_data(
    mif: ImageFormat,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    nifti = Nifti1(get_dummy_nifti(generator.dest_dir / "nifti.nii"))
    with mock.patch.dict(os.environ, {"MRTRIX_CLI_PARSE_ONLY": "0"}):
        mif = ImageFormat.convert(nifti)
    return mif.fspaths


# @extra_implementation(MedicalImage.read_array)
# def mrtrix_read_array(mif: ImageFormat) -> DataArrayType:
#     raise NotImplementedError(
#         "Need to work out how to use the metadata to read the array in the correct order"
#     )
#     data = mif.read_contents(offset=mif.data_offset)
#     array = np.asarray(data)
#     data_array = array.reshape(mif.dims)
#     return data_array
