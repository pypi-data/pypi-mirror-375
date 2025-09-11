"""Test the packages settings validation."""

from ou_container_builder.settings import Packages, PipPackageEntry, PipPackageLists


def test_valid_packages_settings():
    """Test that a valid packages configuration passes."""
    settings = Packages(apt=["curl"], pip=["jupyterlab"])
    assert settings.apt.build == ["curl"]
    assert settings.apt.deploy == ["curl"]
    assert settings.pip.system[0].name == "jupyterlab"
    assert settings.pip.system[0].type == "package"
    assert settings.pip.user[0].name == "jupyterlab"
    assert settings.pip.user[0].type == "package"


def test_default_sources_settings():
    """Test that the default sources settings are correct."""
    settings = Packages()
    assert settings.apt.build == []
    assert settings.apt.deploy == []
    assert settings.pip.system == []
    assert settings.pip.user == []


def test_simple_pip_package_conversion() -> None:
    """Test that the Pip package entry conversion works."""
    settings = PipPackageLists(system=["jupyterlab"])
    assert settings.system == [PipPackageEntry(name="jupyterlab", type="package")]
