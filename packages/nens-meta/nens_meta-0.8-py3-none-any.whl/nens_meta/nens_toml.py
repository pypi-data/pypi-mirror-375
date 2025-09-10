"""Purpose: read and manage the .nens.toml config file"""

import copy
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.items import Table

from nens_meta import __version__, utils


@dataclass
class Option:
    key: str
    description: str
    value_type: type = str
    default: Any = ""


META_FILENAME = ".nens.toml"
KNOWN_SECTIONS: dict[str, list[Option]] = {}
# First key is the section name, the second key/value pair is the variable name and the
# explanation. If the second key ends with "_TRUE"/"_FALSE", this is stripped and will
# be used to treat the value as a boolean with the indicated default.
KNOWN_SECTIONS["meta"] = [
    Option(key="meta_version", description="Version used to generate the config"),
    Option(
        key="project_name",
        description="Project name (normally the name of the directory)",
    ),
    Option(
        key="uses_python",
        description="Whether we use python",
        default=False,
        value_type=bool,
    ),
    Option(
        key="uses_ansible",
        description="Whether we have an ansible dir",
        default=False,
        value_type=bool,
    ),
]
KNOWN_SECTIONS["pyprojecttoml"] = []
KNOWN_SECTIONS["meta_workflow"] = [
    Option(
        key="python_version",
        description="Python version to use for linting and so",
        default="3.12",
    ),
    Option(
        key="run_pytest",
        description="Whether to run pytest in the workflow",
        default=False,
        value_type=bool,
    ),
]

logger = logging.getLogger(__name__)


def write_documentation():
    target = Path(__file__).parent.parent.parent / "doc" / "nens_toml_example.toml"
    lines = []
    for section in KNOWN_SECTIONS:
        lines.append(f"[{section}]")
        for option in KNOWN_SECTIONS[section]:
            lines.append(f"# {option.description}")
            lines.append(f"{option.key} = {repr(option.default)}")
        lines.append("")

    content = "\n".join(lines)
    content = content.replace(" False", " false")  # Toml syntax hack
    target.write_text(content)


def nens_toml_file(project: Path) -> Path:
    return project / META_FILENAME


def create_if_missing(project: Path):
    if not nens_toml_file(project).exists():
        nens_toml_file(project).write_text("")
    our_config = OurConfig(project)
    our_config.read()
    our_config.update_meta_options()
    our_config.write()


def detected_meta_values(project: Path) -> dict[str, str | bool | list]:
    """Return values we can detect about the project, normally set in [meta]"""
    detected: dict[str, str | bool | list] = {}
    detected["uses_python"] = utils.uses_python(project)
    detected["uses_ansible"] = utils.uses_ansible(project)
    detected["meta_version"] = __version__
    name = project.resolve().name
    detected["project_name"] = name
    return detected


class MissingDocumentationError(Exception):
    pass


class OurConfig:
    """Wrapper around a project's .nens.toml

    See https://tomlkit.readthedocs.io/en/latest/quickstart/
    """

    _config_file: Path
    _contents: tomlkit.TOMLDocument
    _project: Path

    def __init__(self, project: Path):
        self._project = project
        self._config_file = nens_toml_file(project)
        self._contents = self.read()
        self.update_meta_options()

    def read(self) -> tomlkit.TOMLDocument:
        return tomlkit.parse(self._config_file.read_text())

    def write(self):
        utils.write_if_changed(
            self._config_file, tomlkit.dumps(self._contents), handle_extra_lines=False
        )

    def update_meta_options(self):
        """Detect meta options"""
        if "meta" not in self._contents:
            self._contents.append("meta", tomlkit.table())
        current: Table = self._contents["meta"]  # type: ignore
        detected = detected_meta_values(self._project)
        must_be_set = ["meta_version"]
        for key, value in detected.items():
            if key not in current:
                current[key] = value
                logger.info(f".nens.toml: suggesting [meta]->{key}")
            if key in must_be_set:
                if current["meta_version"] != detected["meta_version"]:
                    current["meta_version"] = detected["meta_version"]
                    logger.info(".nens.toml: changing [meta]->meta_version")

    def has_section_for(self, section_name: str) -> bool:
        return section_name in KNOWN_SECTIONS

    def section_options(self, section_name: str) -> dict:
        """Return all options configured in a given section, if available."""
        if section_name not in KNOWN_SECTIONS:
            # Force ourselves to document our stuff!
            raise MissingDocumentationError(
                f"Section {section_name} not documented in nens-meta"
            )
        section = self._contents.get(section_name)
        if section is None:
            section = {}
        options: dict[str, str | bool | list] = {}
        for option in KNOWN_SECTIONS[section_name]:
            value = section.get(option.key, copy.deepcopy(option.default))
            if not isinstance(value, option.value_type):
                raise ValueError(
                    f"{option.key} should be of type {option.value_type}, not {type(value)}"
                )
            options[option.key] = value

        # Warn for old/misspelled options.
        known_keys = [option.key for option in KNOWN_SECTIONS[section_name]]
        for key in section:
            if key not in known_keys:
                logger.warning(
                    f"Parameter {key} in section [{section_name}] is not known"
                )
        logger.debug(f"Contents of section {section_name}: {options}")
        return options


if __name__ == "__main__":
    # Only called to write the documentation file.
    write_documentation()
