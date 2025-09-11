# Services

The `services` setting is used to specify operating-system services that should automatically be started when
the VCE starts. Additionally, the user is given the necessary permissions to start, stop, and restart the
services via `sudo`:

:::{code-block} yaml
services:
  - service-name  # The name of the service to start
:::
