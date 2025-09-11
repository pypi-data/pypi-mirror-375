# OU Container Builder

Documentation for the OU Container Builder can be found here: https://docs.ocl.open.ac.uk/container-builder/v3

# Install and Run



## Development

The OU Container Builder has the following dependencies:

* [Python](https://www.python.org/) 3.10 or 3.11 (higher may also work, but is not tested)
* [Hatch](https://hatch.pypa.io/latest/)
* [pre-commit]()

After installing these, use the following command to run the tests

```
hatch run test
```

To run the builder itself use

```
hatch shell
```

and then you can run

```
ocb
```

to run the development version of the code.

### Code Style

The OU Container Builder uses [Black](https://black.readthedocs.io/en/stable/) and [Ruff](https://docs.astral.sh/ruff/)
to enforce a code style.

To automatically check that any committed code follows the code style, install a git pre-commit hook using
the following command:

```
pre-commit install
```
