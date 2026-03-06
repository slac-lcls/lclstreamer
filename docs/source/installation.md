# Installation


## Installing LCLStreamer

LCLStreamer uses [pixi](https://pixi.sh/latest/) for deployment, due to the mixture of
conda and PyPI packages needed by the application.

In order to install LCLStreamer, first
[install pixi](https://pixi.sh/latest/#installation), then run the following command
from the top level folder of the GitHub repository:

``` bash
pixi install
```

This will create virtual python environments, located in the `.pixi` subdirectory, that
contain all the python packages required by LCLStreamer to run, each at a version that
is compatible with the LCLStreamer application.
