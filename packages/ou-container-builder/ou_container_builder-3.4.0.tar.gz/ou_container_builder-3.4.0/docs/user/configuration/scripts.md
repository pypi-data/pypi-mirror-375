# Scripts

The `scripts` setting allows for specifying bash scripts that are executed during the build process
or at VCE startup:

:::{code-block} yaml
scripts:
  - stage:     # The stage at which this script is run
    name:      # Filename for the script - Only for startup scripts
    commands:  # A list of commands to run
:::

The `commands` are written to a file that is then executed via the bash interpreter.

## Build scripts

Build scripts can either be run during the `build` or `deploy` stages of the build process.

The following script would download and extract data from the net, which is then distributed
with the VCE to users:

:::{code-block} yaml
scripts:
  - stage: deploy
    commands:
      - mkdir -p /usr/share/module-data
      - wget -O /usr/share/module-data/source.tar.bz2 https://...
      - cd  /usr/share/module-data
      - tar -jxf source.tar.bz2
:::

## Startup scripts

Startup scripts are run when the VCE starts up. The `name` setting defines the filename, but
is also used to provide progress information to the user. The filename **must** follow the
pattern `RUN_ORDER_NUMBER-FILENAME`, where the `FILENAME` part is what is shown to the user
as progress information. Any `-` in the `FILENAME` part are converted into spaces and the first
letter will be capitalised.

The following script would download a file from a URL and save it as {file}`target-filename`,
while showing the user the message "Downloading image files":

:::{code-block} yaml
scripts:
  - stage: startup
    name: 201-downloading-image-files
    commands:
      - wget -O target-filename https://....
:::

The `RUN_ORDER_NUMBER` must be in the range 201 - 1000, which are {doc}`allocated for user use <../../developer/startup_script_weights>`.
