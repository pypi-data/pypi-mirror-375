# Environment

The `environment` setting allows for the configuration of environment variables. It consists of a list of
name-value pairs, with each name-value pair defining one environment variable and its value. The environment
variables defined here are available both during the build process, as well as when running the VCE.

:::{code-block} yaml
environment:
  - name:   # The environment variable name
    value:  # The environment variable value
:::
