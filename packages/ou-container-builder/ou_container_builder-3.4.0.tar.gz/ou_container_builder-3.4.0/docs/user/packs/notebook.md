# Jupyter Notebook

Use the `notebook` pack to install the [Jupyter Notebook](https://jupyter.org/) interface into the system environment:

:::{code-block} yaml
packs:
  notebook: {}
:::

Use the `server.default_path` setting ({doc}`../configuration/server` settings) set to `/tree` to make
the Notebook interface the default UI to load.

It is possible to restrict the installed Notebook to a major revision:

:::{code-block} yaml
packs:
  jupyterlab:
    version: 7
:::

Currently only version 7 is supported.
