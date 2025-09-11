# Image

The `image` section defines the basic information about the VCE image to build. The `image` section contains the
`base` and `user` keys. If no values are provided, or if the `image` section is not provided, then the following
default values are used:

:::{code-block} yaml
image:
  base: python:3.11-bookworm  # The base image to use for building the VCE image
  user: ou                    # The name of the user that runs the VCE software
:::

:::{note}
In general the `user` setting should only be changed if the aim is to use the container exclusively outside the
OpenComputing Lab or if the base image already has a user set.
:::
