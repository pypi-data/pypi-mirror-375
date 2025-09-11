# Cellist

![PyPI](https://img.shields.io/pypi/v/cellist)
![Downloads](https://pepy.tech/badge/cellist)
![Documentation Status](https://readthedocs.org/projects/cellist/badge/?version=latest)

Cell identification in high-resolution Spatial Transcriptomics

Cellist is a computational method to perform cell segmentation on high-resolution spatial transcriptomics (ST) data, including sequncing-based (e.g. Stereo-seq and Seq-Scope) and imaging-based (e.g. seqFISH+ and STARmap) technologies.

![avatar](docs/_static/img/Cellist_workflow.png)

## Change Log
### v0.0.1a
* Build Cellist.
### v1.0.0
* Release Cellist.
### v1.1.0
* Update Cellist model.
* Support Cellpose for image-based segmentation.
### v1.1.1
* Fix a typo in the Watershed segmentation.
* Update package dependencies.

## System Requirements
### Hardware Requirements
For optimal performance, especially when using `Cellpose` for initial image-based segmentation, a system with a GPU is recommended.

### Operating System
This package is supported on Linux systems and has been tested on **Rocky Linux release 9.4**.

### Python Rependencies
The core dependencies include:
```
scikit-learn>=1.3.1
scikit-image>=0.20.0
h5py>=3.8.0
tables>=3.7.0
```
A complete list of required packages is available in `requirements.txt`.

## Install Cellist
### Step-by-step Instructions
We recommend installing Cellist in a fresh conda environment:
```bash
git clone https://github.com/wanglabtongji/Cellist.git
cd Cellist
conda create -n Cellist python=3.10
conda activate Cellist
pip install -r requirements.txt
pip install .
```
Note: After installation, users can verify the installation by running `cellist --help`. The command may return a message such as `fastpd is not installed. Please compile the fastpd library`. This warning originates from Spateo and does not affect the functionality of `Cellist`.

### Typical Install Time
On a high-performance server, installation typically takes 10 minutes.

## Documentation
For full installation and usage of Cellist, please refer to the [documentation](https://cellist.readthedocs.io/en/latest/).

## Usage
```bash
cellist --help
usage: cellist [-h] [-v] {seg,align,watershed,cellpose,impute} ...

Cellist (Cell identification in high-resolution Spatial Transcriptomics) is a cell segmentation tool for high-
resolution spatial transcriptomics.

positional arguments:
  {seg,align,watershed,cellpose,impute}
    seg                 Run Cellist segmentation on high-resolution spatial transcriptomics.
    align               Refine alignment between image and spatial transcriptomics.
    watershed           Run initial watershed segmentation on the staining image.
    cellpose            Run initial cellpose segmentation on the staining image.
    impute              Perform spatially-aware gene imputation within each cluster.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Print version info.
```
