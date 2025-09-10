import os
import urllib.parse
import urllib.request
from typing import Iterable
from typing import Optional
from typing import Union

from silx.io.url import DataUrl

from darfix.core.dataset import ImageDataset


def load_process_data(
    filenames: Union[str, Iterable[str], DataUrl],
    root_dir: Optional[str] = None,
    in_memory: bool = True,
    dark_filename: Optional[Union[str, DataUrl]] = None,
    copy_files: bool = True,
    isH5: bool = False,
    title: str = "",
    metadata_url=None,
):
    """
    Loads data from `filenames`.
    If `filenames` is:

        - a str: consider it as a file pattern (for EDF files).
        - an iterable: consider a list of EDF files.
        - a DataUrl: consider it readable by silx `get_data` function

    :param filenames: filenames to be loaded.
    :param metadata_url: path to the scan metadata for HDF5 containing positioner information in order to load metadata for non-edf files
    """
    indices = li_indices = None
    root_dir_specified = bool(root_dir)
    if isinstance(filenames, Iterable) and not isinstance(filenames, str) and isH5:
        assert len(filenames) == 1
        filenames = filenames[0]

    if isinstance(filenames, DataUrl):
        assert filenames.file_path() not in (
            "",
            None,
        ), "no file_path provided to the DataUrl"
        if not root_dir_specified:
            root_dir = os.path.dirname(filenames.file_path())
        dataset = ImageDataset(
            _dir=root_dir,
            first_filename=filenames,
            in_memory=in_memory,
            copy_files=copy_files,
            isH5=isH5,
            title=title,
            metadata_url=metadata_url,
        )
    elif isinstance(filenames, str):
        if not filenames:
            raise ValueError("'filenames' cannot be an empty string")
        if not root_dir_specified:
            root_dir = _get_root_dir(filenames)
        dataset = ImageDataset(
            _dir=root_dir,
            first_filename=filenames,
            in_memory=in_memory,
            copy_files=copy_files,
            isH5=isH5,
            title=title,
            metadata_url=metadata_url,
        )
    elif isinstance(filenames, Iterable):
        filenames = list(filenames)
        if not root_dir_specified:
            root_dir = _get_root_dir(filenames[0])
        dataset = ImageDataset(
            _dir=root_dir,
            filenames=filenames,
            in_memory=in_memory,
            copy_files=copy_files,
            isH5=isH5,
            title=title,
            metadata_url=metadata_url,
        )
    else:
        raise TypeError(
            f"Expected filenames to be a list, a string or a silx DataUrl. Got {type(filenames)} instead."
        )

    if not dark_filename:
        bg_dataset = None
    elif isinstance(dark_filename, str):
        dark_root_dir = os.path.join(dataset.dir, "dark")
        os.makedirs(dark_root_dir, exist_ok=True)
        bg_dataset = ImageDataset(
            _dir=dark_root_dir,
            first_filename=dark_filename,
            copy_files=False,
            isH5=isH5,
            metadata_url=None,
        )
    elif isinstance(dark_filename, DataUrl):
        assert dark_filename.file_path() not in (
            "",
            None,
        ), "no file_path provided to the DataUrl"
        dark_root_dir = os.path.join(dataset.dir, "dark")
        os.makedirs(dark_root_dir, exist_ok=True)
        bg_dataset = ImageDataset(
            _dir=dark_root_dir,
            first_filename=dark_filename,
            copy_files=False,
            isH5=isH5,
            metadata_url=None,
        )
    else:
        raise TypeError(
            f"Expected dark_filename to be a string or a silx DataUrl. Got {type(dark_filename)} instead."
        )

    assert dataset.data is not None and dataset.data.size > 0, "No data was loaded!"

    return dataset, indices, li_indices, bg_dataset


def _get_root_dir(filename: str) -> str:
    url = urllib.parse.urlparse(filename, scheme="file")
    return os.path.dirname(urllib.request.url2pathname(url.path))
