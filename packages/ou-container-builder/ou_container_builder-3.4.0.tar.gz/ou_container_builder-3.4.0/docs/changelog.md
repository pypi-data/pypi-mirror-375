# Changelog

## 3.0

## 3.4.0

* **Update**: Allow startup script to run without a web server

## 3.3.0

* **Update**: Updated code-server to v4.103.0

### 3.2.2

* **Bugfix**: Fix home-directory startup bug
* **Bugfix**: Fix an error when reporting config file errors

### 3.2.1

* **Bugfix**: Further fix to file ownership handling

### 3.2.0

* **Update**: Automatically generate the token from the module settings
* **Bugfix**: Fix an issue with error handling in file ownership
* **Deprecation**: Deprecate server.wrapper_host settings

### 3.1.0

* **Update**: Install user packages globally
* **Bugfix**: Add $HOME/.local/bin to the PATH
* **Bugfix**: Ensure the startup websocket connection is kept open

### 3.0.0

* **Breaking**: Switched to using Buildah as the build backend
* **New**: Two-stage build process
* **New**: Added support for Notebook v7
* **New**: Added support for remote desktops with XFCE
* **New**: Added support for external packs
* **Update**: Updated JupyterLab to v4
* **Removed**: Removed support for Notebook v6 pack
* **Removed**: Removed support for Tutorial Server pack
* **Removed**: Removed support for the MariaDB pack

## 2.0

### 2.7.2

* **Bugfix**: Disable installation from piwheels

### 2.7.1

* **Bugfix**: Correctly handle content paths with spaces

### 2.7.0

* **Update**: Bump jupyterhub to 3.x

### 2.6.3

* **New**: Hide the upgrade banner in the nbclassic pack

### 2.6.2

* **New**: Added branding to the nbclassic pack

### 2.6.1

* **Update**: Update ou_container_launcher to >= 1.2.0

### 2.6.0

* **New**: Add rustc as a core install

### 2.5.0

* **Update**: Allow the user to restart any services

### 2.4.0

* **New**: Added support for specifying whether an apt key needs dearmoring

### 2.3.0

* **New**: Added support for specifying code_server extensions
* **New**: Added support for specifying the code_server version

### 2.2.1

* **Bugfix**: Correct minimum/maximum specifiers on python packages

### 2.2.0

* **Update**: Support the full set of configuration options in jupyter-server-proxy
* **Bugfix**: Fix validation error messages not being shown

### 2.1.0

* **Update**: Added some base settings
* **Update**: Update nbclassic to >= 0.4.8
* **Bugfix**: Fixed a typo in the Notebook config

### 2.0.1

* **Bugfix**: Fixed a bug in the sudo configuration for older OSes

### 2.0.0

* **New**: Explicit support for JupyterLab and NBClassic
* **Breaking**: Major changes to the configuration file format

## 1.0

### 1.0.9

* **Update**: Dependencies updated

### 1.0.8

* **Bugfix**: Fixed a bug in the mariadb startup script

### 1.0.7

* **Bugfix**: Security upgrades in dependencies

### 1.0.6

* **Update**: Upgrade the tutorial-server to 1.0.2

### 1.0.5

* **Update**: Upgrade the tutorial-server to 1.0.0
* **Update**: upgraded the ou-container-content to 1.1.0

### 1.0.4

* **Update**: Upgraded the ou-container-content to 1.0.4

### 1.0.3

* **Update**: Upgraded the ou-container-content to 1.0.3

### 1.0.2

* **Update**: Upgraded the ou-container-content to 1.0.2

### 1.0.1

* **Update**: Upgrade the ou-container-content to 1.0.1

### 1.0.0

* **Update**: Upgrade the ou-container-content to 1.0.0

### 1.0.0b2

* **Update**: Upgrade the ou-container-content to 1.0.0-b2

### 1.0.0-b1

* **New**: Initial release
