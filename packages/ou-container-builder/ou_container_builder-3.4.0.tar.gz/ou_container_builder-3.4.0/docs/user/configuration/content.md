# Content

The `content` setting is used to distribute content with the VCE to the user. It contains a list configuring the
source and target of the content, as well as whether the content should be overwritten, if it already exists:

:::{code-block} yaml
content:
  - source: content/notebooks  # The path to copy the content from
    target: notebooks          # The path to copy the content to
    overwrite: never           # Whether to overwrite existing data
:::

## `source`

The `source` is always interpreted as relative to the location of the {file}`ContainerConfig.yaml`.

## `target`

If the `target` is a relative path, then it is interpreted as relative to the VCE user's home directory. Thus

:::{code-block} yaml
content:
  - source: content/notebooks
    target: notebooks
    overwrite: never
:::

will copy the contents of the {file}`content/notebooks` directory into the `notebooks` directory in the VCE
user's home directory.

To copy content directly into the VCE user's home directory specify an empty `target`:

:::{code-block} yaml
content:
  - source: home
    target: ""
    overwrite: never
:::

Copying of the content will take place when the VCE starts.

If the `target` is an absolute path, then the content will be copied to that location during the build process.
This can be useful to copy any files that are needed for {doc}`scripts` or to distribute data that the VCE user
should not be able to change. When using an absolute path, the `overwrite` setting is ignored and the files are
always copied and overwritten.

## `overwrite`

The `overwrite` setting can either be set to `never` or to `always`. If set to `never`, then when copying files,
if that file already exists, it is not overwritten with the version distributed with the VCE. If set to `always`
any existing files will always be overwritten.

In either case, files that have previously been distributed will never be automatically deleted.
