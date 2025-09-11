# Sources

The `sources` setting is used to configure additional sources from which to install packages.
All sources configured using this approach **must** be signed and the signing key **must** be
available online:

:::{code-block} yaml
sources:
  apt:
    - name:            # The name of the source - used for filenames
      key_url:         # The URL from which to fetch the signing key
      dearmor: true    # Whether to automatically dearmor the signing key
      deb:             # The DEB line
        url:           # The URL for the DEB line
        distribution:  # The distribution for the DEB line
        component:     # The component for the DEB line
:::

The `name` is used for generating filenames, thus it **must** be unique within the configuration.
