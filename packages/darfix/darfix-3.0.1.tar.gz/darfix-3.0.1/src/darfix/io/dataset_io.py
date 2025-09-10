__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "12/06/2020"

import json

import numpy
from silx.io import fabioh5
from silx.io.url import DataUrl

from darfix.core.dataset import Data
from darfix.core.dataset import ImageDataset
from darfix.core.dimension import AcquisitionDims


def save_to_json(
    filename, dataset, original_dataset=None, hi_indices=None, li_indices=None
):
    my_dict = {}
    my_dict["dir"] = dataset.dir
    my_dict["dataset"] = [url.file_path() for url in dataset.get_data().urls]
    my_dict["shape"] = dataset.data.shape
    my_dict["in_memory"] = dataset.in_memory
    if original_dataset is not None:
        my_dict["original_dataset"] = [
            url.file_path() for url in original_dataset.get_data().urls
        ]
    if hi_indices is not None:
        my_dict["hi_indices"] = hi_indices.tolist()
    if li_indices is not None:
        my_dict["li_indices"] = li_indices.tolist()
    if dataset.dims.ndim > 0:
        my_dict["dims"] = dataset.dims.to_dict()
    with open(filename + ".json", "w") as f:
        json.dump(my_dict, f)


def load_from_json(filename):
    hi_indices = li_indices = dims = None
    with open(filename + ".json", "r") as f:
        distro = json.load(f)
        urls = numpy.array(
            [DataUrl(file_path=url, scheme="fabio") for url in distro["dataset"]]
        )
        if "original_dataset" in distro:
            original_dataset = distro["original_dataset"]
        else:
            original_dataset = distro["dataset"]
        metadata = []
        for filename in original_dataset:
            fabio_reader = fabioh5.EdfFabioReader(file_name=filename)
            metadata.append(fabio_reader)
            fabio_reader.close()
        metadata = numpy.array(metadata)
        hi_indices = distro["hi_indices"] if "hi_indices" in distro else None
        li_indices = distro["li_indices"] if "li_indices" in distro else None
        if "dims" in distro:
            dims = AcquisitionDims()
            dims.from_dict(distro["dims"])
        else:
            dims = None
        data = Data(urls, metadata, distro["in_memory"]).reshape(distro["shape"])
        dataset = ImageDataset(
            _dir=distro["dir"], data=data, in_memory=distro["in_memory"], dims=dims
        )

    return dataset, hi_indices, li_indices
