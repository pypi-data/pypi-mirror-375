# Module

The `module` section defines the module information, which is used to create the home directory structure,
which ensures that there are no potential conflicts between VCEs. The `module` section contains the following
two keys, which both have to have a value:

:::{code-block} yaml
module:
  code:          # The module's code
  presentation:  # The presentation this VCE is for
:::
