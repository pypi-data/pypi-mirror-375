import json
import subprocess
from pathlib import Path
from typing import List, Dict, Union


def write(file: Union[str, Path], tags: List[str]):
    """Write image metadata tags to an image file using ExifTool. Existing file
    will be overwritten.

    :param file: Path to image file.
    :param tags: List of ExifTool tag assignment strings.
    """
    # Setup metadata copy
    cmd = ['exiftool', '-q', '-overwrite_original', str(file)]

    # Map all the other tags
    cmd.extend(tags)

    # Run exiftool
    subprocess.run(cmd, check=True)


def copy_all(src: Union[str, Path], dest: Union[str, Path],
             extra_tags: List[str] = None, overwrite=True):
    """Copy tag metadata from source image to destination image.

    :param src: Path to image file containing source metadata.
    :param dest: Path to destination image file.
    :param extra_tags: If provided, write additional tags to :code:`dest`.
    :param overwrite: If :code:`True`, overwrite the destination image file.
    """
    # Setup metadata copy
    cmd = ['exiftool', '-q']

    # Overwrite original destination file
    if overwrite:
        cmd.append('-overwrite_original')

    # Skip tags that don't make sense in JPGs
    if dest.suffix not in ['.tif', '.tiff']:
        cmd.extend(['-XMP-tiff:all=', '-ExifIFD:BitsPerSample=',
                    '-IFD0:BitsPerSample='])

    # Original tags from original files
    cmd.extend(['-TagsFromFile', str(src)])

    # Map all the other tags
    cmd.append('-all:all')

    # Project specific tags
    if extra_tags is not None:
        cmd.extend(extra_tags)

    # Add target
    cmd.append(str(dest))

    # Run exiftool
    subprocess.run(cmd, check=True)


def read_tags(file: Union[str, Path, List[Path]], tags: List[str] = None) -> \
        List[Dict]:
    """Get metadata tags for a file or list of files.

    :param file: Path or list of Paths to image files
    :param tags: List of ExifTool tag strings, e.g.
           :code:`['-ExposureTime', '-ISO']`
    :return: List of dicts containing tag values, one dict for each input path
    """
    # Setup metadata request
    cmd = ['exiftool', '-J']

    # Append all the other tags
    if tags is not None:
        cmd.extend(tags)

    # Append all input files
    if isinstance(file, str):
        cmd.append(file)
    if isinstance(file, Path):
        cmd.append(str(file))
    elif isinstance(file, list):
        cmd.extend([str(f) for f in file])
    else:
        raise ValueError(f'Unsupported type for argument file: {type(file)}')

    # Run exiftool
    res = subprocess.run(cmd, check=True, capture_output=True, text=True)

    # Convert from JSON
    return json.loads(res.stdout)
