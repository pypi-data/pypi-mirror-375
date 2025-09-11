# Jupyter Server Configuration

The `jupyter_server_config` allows configuring the core Jupyter Server that runs the VCE, but also any
packages from the Jupyter ecosystem that support configuration via the {file}`jupyter_server_config.json`:

:::{code-block} yaml
jupyter_server_config:
  config: value
:::

Available options for the Jupyter Server [can be found here](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html).
