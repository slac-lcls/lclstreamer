# Installation / Running


## Installing LCLStreamer

LCLStreamer uses [pixi](https://pixi.sh/latest/) for deployment, due to the mixture of
conda and PyPI packages needed by the application.

In order to install LCLStreamer, first
[install pixi](https://pixi.sh/latest/#installation), then run the following command
from the top level folder of the GitHub repository:

``` bash
pixi install
```

This will create a virtual environment, located in the `.pixi` subdirectory, that
contains all the python packages required by LCLStreamer to run, each at a version that
is compatible withthe LCLStreamer application.


## Running LCLStreamer

LCLStreamer is currently designed to run exclusively using the MPI protocol. After
installing LCLStreamer, the appliaction can be launched using the `pixi run` command.
For example:

``` bash
pixi run mpirun -n 8 lclstreamer
```

LCLStreamer looks for a configuration file named `lclstreamer.yaml` in the current
working directory. Alternatively, the path to the configuration file can be passed to
the lclstreamer executable using the --config option:

``` bash
pixi run mpirun -n 8 lclstreamer --config examples/lclstreamer.yaml
```
