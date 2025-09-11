# JupyterLab

Use the `jupyterlab` pack to install the [JupyterLab](https://jupyter.org/) interface into the system environment:

:::{code-block} yaml
packs:
  jupyterlab: {}
:::

Use the `server.default_path` setting ({doc}`../configuration/server` settings) set to `/lab` to make
the JupyterLab interface the default UI to load.

It is possible to restrict the installed JupyterLab to a major revision:

:::{code-block} yaml
packs:
  jupyterlab:
    version: 4
:::

Currently only version 4 is supported.
