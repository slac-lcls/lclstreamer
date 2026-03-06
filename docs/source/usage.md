# Usage


## Basic Usage

LCLStreamer is currently designed to run exclusively using the MPI protocol. After
installing LCLStreamer, the application can be launched using the `pixi run` command.
For example:

``` bash
pixi run mpirun -n 8 lclstreamer
```

LCLStreamer looks for a configuration file named `lclstreamer.yaml` in the current
working directory. Alternatively, the path to the configuration file can be passed to
the lclstreamer executable using the --config option:

``` bash
pixi run mpirun -n 8 lclstreamer --config examples/lclstreamer-internal.yaml
```

This command starts LCLStreamer using an internal event source, which does not
depend on any facility framework, generates random data, and is perfect for testing.


## Running LCLStreamer with the psana1 and psana2 frameworks

When running LCLStreamer using one of the facility data retrieval frameworks (`psana1`
or `psana2`), a Python environment which contains the required framework must be
specified in the launching command.

For example, for the `psana1` framework:

``` bash
pixi run --environment psana1 mpirun -n 8 lclstreamer --config examples/lclstreamer-psana1.yaml
```

And for the `psana2`:

``` bash
pixi run --environment psana2 mpirun -n 8 lclstreamer --config examples/lclstreamer-psana2-mfx.yaml
```
