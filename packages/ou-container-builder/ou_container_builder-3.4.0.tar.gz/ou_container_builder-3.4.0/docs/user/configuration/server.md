# Server

The `server` settings configure the core server that provides the VCE interface. The block below shows the
available settings with their default values:

:::{code-block} yaml
server:
  default_path: "/"             # The default URL path that the user will be redirected to
  access_token:                 # The access token used for authentication when running locally
  wrapper_host: "*.open.ac.uk"  # The host name that embeds this VCE
:::

Any settings that are not provided are replaced with their default values.

## `default_path`

The following `default_path` values will work, depending on which {doc}`../packs/index` are enabled:

* {doc}`JupyterLab <../packs/jupyterlab>` - `"/lab"`
* {doc}`JupyterLab <../packs/notebook>` - `"/tree"`
* {doc}`Code Server <../packs/code_server>` - `"/code-server"`
* {doc}`XFCE4 <../packs/xfce4>` - `"/desktop"`

If you configure any {doc}`web_apps`, then any paths configured there can also be used as the `default_path`.

## `access_token`

The `access_token` is only used when the user accesses the VCE outside of the OCL. When running inside the OCL,
then authentication is handled transparently. It should be set to the pattern `MODULE_CODE-PRESENTATION` all in
uppercase for standardisation across the OCL.

If no `access_token` is set, then a random token is generated each time the user starts the VCE locally and output
on the console. Depending on how the user starts the VCE, this might not be visible to the user, so setting the
`access_token` is strongly recommended.

::::{versionchanged} 3.2.0
If not specified, this setting now defaults to the upper-case value of concatenating the `module.code` and
`module.presentation` settings (see {doc}`./module`) with a hyphen.

So the settings

:::{code-block} yaml
module:
  code: XY123
  presentation: 99J
:::

will result in a default value of `XY123-99J`.
::::

## `wrapper_host`

:::{deprecated} 3.2.0
Due to changes in the Container Launcher, this setting no longer has any effect and will be removed in version **4**.
:::

Unless you are planning to host the VCE outside of the OCL, there is no need to include this setting as the
default is correctly set up for the OCL.
