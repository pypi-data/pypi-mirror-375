# Packages

The `packages` setting is used to configure packages to install into the VCE image. Currently the apt
and pip package managers are supported:

:::{code-block} yaml
packages:
  apt:  # Packages to install via the Debian APT package manager
  pip:  # Packages to install via the Python PIP package manager
:::

Both `apt` and `pip` setting are optional and must not be specified if no packages are to be installed
via the respective package manager.

## `apt`

Use this setting to configure additional packages to install via the `apt` package manager.

The OU Container Builder uses a two-stage process to create the VCE image. The first, the `build` stage
is used to compile and build any custom packages and software to install. The second, the `deploy` stage
is used to construct the final VCE image that is then distributed. This ensures that the resulting VCE
image is as small as possible.

You can specify which packages to install into each of the two stages:

:::{code-block} yaml
packages:
  apt:
    build:            # List of packages to be installed into the build phase
      - package-name
    deploy:           # List of packages to be installed into the deploy phase
      - package-name
:::

As in most cases the aim is to install the software needed when running the VCE, you will mostly specify
packages in the `deploy` setting. Specifying packages in the `build` setting is only necessary if you
want to run {doc}`scripts` during the build process and need additional packages for that.

If you need to install packages from outside the default package sources, you can configure
{doc}`additional sources <sources>`.
## `pip`

Use this setting to configure additional packages to install via the `pip` package manager.

VCEs created with the OU Container Builder have two separate python environments. The `system` environment
contains the python packages needed to create the user interface used by the VCE. The VCE user cannot install
any packages into this environment. The `user` environment contains the python packages used by the user. The
reason for this split is that it ensures that the VCE user cannot accidentally install python packages that
prevent the VCE from starting.

:::{code-block} yaml
packages:
  pip:
    system:                               # List of packages to be installed into the system environment
      - package-name or requirement file
    user:                                 # List of packages to be installed into the user environment
      - package-name or requirement file
:::

Any packages needed to extend the user interface, for example JupyterLab extensions, **must** be installed into
the `system` environment. Any packages the VCE user will need when running software, for example when running
a notebook, **must** be installed into the `user` environment.

::::{important}

It is generally recommended that you explicitly restrict the versions of the packages to install. This can
either be done by pinning to a specific version, such as here where the version of `scipy` is restricted to
1.13.0:

:::{code-block} yaml
packages:
  pip:
    user:
      - scipy==1.13.0
:::

Or by using semantic versioning to limit the allowed package versions to those that will not introduce
breaking changes, such as here, where `scipy` cannot be upgraded to versions in the 2.x.y family:

:::{code-block} yaml
packages:
  pip:
    user:
      - scipy>=1.13.0,<2
:::

::::

:::{warning}
You should install all python packages using the `pip` setting. Do not use scripts to install python packages
at a latter point. This ensures that all python packages are installed in a single step and that the pip package
manager can correctly sort out all dependencies and install versions that are compatible. This also ensures that
any incompatabilities are discovered when the VCE image is built.
:::

### Requirements files

The `pip` setting also supports using requirements.txt files to specify the packages to install. When using this
functionality, you need to explicitly specify the filename via the `name` key and `requirements.txt` via the `type`
key:

:::{code-block} yaml
packages:
  pip:
    system:
      - name: jupyterlab-extensions.txt
        type: requirements.txt
:::
