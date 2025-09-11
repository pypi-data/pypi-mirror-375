# Configuration

The OU Container Builder is configured via the {file}`Configuration.yaml` file. The details of the settings for this
configuration file are documented in this section.

The {file}`Configuration.yaml` has only two required settings. The [Module](module) settings and the `version`, which
**must** be set to `"3"`:

:::{code-block} yaml
version: "3"
:::

Additionally, the OU Container Builder supports extending the functionality and configuration file through
{doc}`../packs/index`.

The {file}`Configuration.yaml` contains the following sections:

:::{tableofcontents}
:::
