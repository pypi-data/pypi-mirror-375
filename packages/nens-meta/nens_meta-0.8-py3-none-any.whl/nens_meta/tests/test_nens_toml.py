"""Tests for update_project.py"""

from pathlib import Path

import pytest

from nens_meta import nens_toml


def test_nens_toml_file(tmp_path: Path):
    assert nens_toml.nens_toml_file(tmp_path).name == ".nens.toml"


def test_create_if_missing(tmp_path: Path):
    nens_toml.create_if_missing(tmp_path)
    assert (tmp_path / ".nens.toml").exists()


def test_init(tmp_path: Path):
    nens_toml.nens_toml_file(tmp_path).write_text("year = 1972")
    config = nens_toml.OurConfig(tmp_path)
    assert config._contents["year"] == 1972


def test_write(tmp_path: Path):
    nens_toml.nens_toml_file(tmp_path).write_text("year = 1972")
    config = nens_toml.OurConfig(tmp_path)
    config._contents["month"] = 12
    config.write()
    assert "month = 12" in nens_toml.nens_toml_file(tmp_path).read_text()


def test_section_options1(tmp_path: Path):
    # Properly read a known variable in a known section.
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    project_name = "1972"
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    assert config.section_options("meta")["project_name"] == "1972"


def test_section_options2(tmp_path: Path):
    # Barf upon an unknown/undocumented section.
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [reinout]
    year = 1972
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    with pytest.raises(nens_toml.MissingDocumentationError):
        config.section_options("reinout")


def test_section_options3(tmp_path: Path):
    # Don't return values that are unknown.
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    year = 1972
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    assert "year" not in config.section_options("meta").keys()


def test_section_options_boolean1(tmp_path: Path):
    # Handle boolean values (those have _TRUE or _FALSE prepended)
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    uses_python = true
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    assert config.section_options("meta")["uses_python"] is True


def test_section_options_boolean2(tmp_path: Path):
    # Handle default for boolean values
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    # uses_python has a default of false
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    assert config.section_options("meta")["uses_python"] is False


def test_section_options_boolean3(tmp_path: Path):
    # Complain if a boolean value has a non-boolean value.
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    uses_python = "1972"
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    with pytest.raises(ValueError):
        config.section_options("meta")["uses_python"]


def test_update_meta_options1(tmp_path: Path):
    # Create a new "meta" section if it is missing.
    nens_toml.nens_toml_file(tmp_path).write_text("")
    config = nens_toml.OurConfig(tmp_path)
    # the init automatically calls config.update_meta_options()
    assert "meta" in config._contents


def test_update_meta_options2(tmp_path: Path):
    # version and so is filled in in an updated file.
    nens_toml.nens_toml_file(tmp_path).write_text("")
    config = nens_toml.OurConfig(tmp_path)
    # the init automatically calls config.update_meta_options()
    meta_section = config.section_options("meta")
    assert "meta_version" in meta_section
    assert "project_name" in meta_section


def test_update_meta_options4(tmp_path: Path):
    # The version should always be updated.
    nens_toml.nens_toml_file(tmp_path).write_text(
        """
    [meta]
    meta_version = "1972"
    """
    )
    config = nens_toml.OurConfig(tmp_path)
    assert config.section_options("meta")["meta_version"] != "1972"


def test_write_documentation():
    nens_toml.write_documentation()
