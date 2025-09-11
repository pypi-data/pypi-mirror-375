# Code Server

The `code_server` pack installs the [Code Server](https://github.com/coder/code-server) VS Code into the VCE.

To install the `code_server` pack with its default settings use the following snippet:

:::{code-block} yaml
packs:
  code_server: {}
:::

Use the `server.default_path` setting ({doc}`../configuration/server` settings) set to `/code-server` to make
the Code Server the default UI to load.

It is possible to also pin a specific version and specify extensions to install:

:::{code-block} yaml
packs:
  code_server:
    version: 4.23.0     # The version to install
    extensions:         # List of extensions to install
      - extension-name
:::
