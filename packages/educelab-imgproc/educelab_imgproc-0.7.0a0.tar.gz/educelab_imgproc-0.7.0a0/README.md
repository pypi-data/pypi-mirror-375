# EduceLab Image Processing

`educelab-imgproc` is a Python module for performing common image
processing tasks. This module is largely a collection of wrapper functions
around functionality provided by other toolkits (numpy, scikit-image, etc.) and
is meant to encourage consistent, predictable use across EduceLab projects.
It should not be considered a total replacement for those other, wonderful
toolkits.

## Requirements
- Python 3.9+

## Installation

This project is available on PyPI:

```shell
python3 -m pip install educelab-imgproc
```

### GUI (Work in progress)

This package comes with a basic image editor for testing the various processing 
functions. To run:

```shell
# Install this module with GUI dependencies
python -m pip install educelab-imgproc[gui]

# Run the GUI
el_imgproc
```

## API Documentation

Visit our API documentation [here](https://educelab.gitlab.io/educelab-imgproc/).