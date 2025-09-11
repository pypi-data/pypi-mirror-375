# XFCE4

Use the `xfce4` pack to install [XFCE4](https://www.xfce.org/) and the
[Jupyter Remote Desktop Proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy) into the VCE:

:::{code-block} yaml
packs:
  xfce4: {}
:::

This provides a full XFCE4 desktop GUI, made available through a browser-based VNC remote desktop interface.

Use the `server.default_path` setting ({doc}`../configuration/server` settings) set to `/desktop` to make
the XFCE4 interface the default UI to load.
