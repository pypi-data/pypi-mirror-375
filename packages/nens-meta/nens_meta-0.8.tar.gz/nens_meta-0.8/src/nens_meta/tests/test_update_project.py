"""Tests for update_project.py"""

from pathlib import Path

import pytest

from nens_meta import nens_toml, update_project


def test_check_prerequisites1(tmp_path: Path):
    with pytest.raises(SystemExit):
        # Missing .git/
        update_project.check_prerequisites(tmp_path)


def test_check_prerequisites2(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    with pytest.raises(SystemExit):
        # Missing .nens.toml
        update_project.check_prerequisites(tmp_path)


# TemplatedFile is tested through EditorConfig, btw
def test_editor_config1(tmp_path: Path):
    # No config, check file contents.
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    editor_config = update_project.Editorconfig(tmp_path, our_config)
    assert "geojson" in editor_config.content


def test_editor_config2(tmp_path: Path):
    # No config, check file contents of the written file
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    editor_config = update_project.Editorconfig(tmp_path, our_config)
    editor_config.write()
    assert "geojson" in (tmp_path / ".editorconfig").read_text()


def test_dependabot(tmp_path: Path):
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    dependabot_yml = update_project.DependabotYml(tmp_path, our_config)
    assert "interval" in dependabot_yml.content
    dependabot_yml.write()


def test_metaworkflowyml(tmp_path: Path):
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    meta_workflow_yml = update_project.MetaWorkflowYml(tmp_path, our_config)
    assert "workflow_dispatch" in meta_workflow_yml.content
    meta_workflow_yml.write()


def test_requirements_yml1(tmp_path):
    # requirements.yml should be created if it doesn't exist yet.
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    requirements_yml = update_project.RequirementsYml(tmp_path, our_config)
    requirements_yml.write()
    content = (tmp_path / "requirements.yml").read_text()
    assert "ansible.posix" in content


def test_requirements_yml2(tmp_path: Path):
    # requirements.yml should only be created if it doesn't exist yet.
    nens_toml.create_if_missing(tmp_path)
    existing_file = tmp_path / "requirements.yml"
    existing_file.write_text("Hurray, some existing content")
    our_config = nens_toml.OurConfig(tmp_path)
    requirements_yml = update_project.RequirementsYml(tmp_path, our_config)
    requirements_yml.write()
    content = (tmp_path / "requirements.yml").read_text()
    assert "ansible.posix" not in content
    assert "Hurray" in content


def test_requirements_yml(tmp_path):
    # requirements.yml should be only be created if it doesn't exist yet, so there
    # should not be the "Extra lines below are preserved" instruction in there.
    nens_toml.create_if_missing(tmp_path)
    our_config = nens_toml.OurConfig(tmp_path)
    requirements_yml = update_project.RequirementsYml(tmp_path, our_config)
    requirements_yml.write()
    content = (tmp_path / "requirements.yml").read_text()
    assert "Extra lines below" not in content
