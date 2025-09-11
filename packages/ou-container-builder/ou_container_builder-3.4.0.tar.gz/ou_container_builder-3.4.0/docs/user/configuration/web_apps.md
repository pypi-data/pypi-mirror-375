# Web Apps

The `web_apps` setting is used to configure additional web applications that are run via the
[Jupyter Server Proxy](https://jupyter-server-proxy.readthedocs.io). If a web application is
configured here, then a compatible version of the Jupyter Server Proxy is automatically installed.

:::{code-block} yaml
web_apps:
  - path: /my-web-app   # The path at which the web application will be served
    options:            # The proxy configuration settings
:::

The `path` must be unique within the VCE and must not be a path used by any other {doc}`pack <../packs/index>`
installed in the VCE.

The `options` contains a dictionary of settings that is passed directly to the Jupyter Server Proxy.
The full set of available settings [can be found here](https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html).
