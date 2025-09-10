import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

EXTRA_LINES_MARKER = "### Extra lines below are preserved ###\n"
LEAVE_ALONE_MARKER = "NENS_META_LEAVE_ALONE"
SUGGESTION_SUFFIX = ".suggestion"


def strip_whitespace(content: str) -> str:
    """Return content stripped of EOL whitespace and extra EOF linefeeds

    Generating files using jinja2 template tags sometimes result in such unneeded
    whitespace. Stripping it off afterwards is easier than trying to get it right with
    jinja2.
    """
    # Get rid of spaces at the end of lines.
    content = re.sub(r"\ +\n", r"\n", content)
    # Get rid of empty lines at the end.
    content = content.strip() + "\n"
    return content


def _extract_extra_lines(content: str) -> str:
    """Return content after the extra lines marker"""
    parts = content.split(EXTRA_LINES_MARKER)
    if len(parts) > 1:
        return parts[1]
    else:
        return ""


def write_if_changed(target: Path, desired_content: str, handle_extra_lines=True):
    """Write content to file if different, not if it is the same

    And create the file if it doesn't exist.

    And... look for an end-of-generated-file marker and preserve the contents after
    it. If `handle_extra_lines` is True (the default).

    And... leave it alone if the marker is there.

    """
    existing_content = target.read_text() if target.exists() else ""
    leave_alone = LEAVE_ALONE_MARKER in existing_content
    if handle_extra_lines:
        extra_lines = _extract_extra_lines(existing_content)
        extra_lines_marker_with_empty_line_before = "\n" + EXTRA_LINES_MARKER
        new_content = extra_lines_marker_with_empty_line_before.join(
            [desired_content, extra_lines]
        )
    else:
        new_content = desired_content

    if new_content == existing_content:
        logger.debug(f"{target} remained the same")
        return

    if leave_alone:
        logger.debug(f"Leave-alone marger found in {target}")
        target = target.parent / (target.name + SUGGESTION_SUFFIX)

    target.write_text(new_content)
    logger.info(f"Wrote {target}")


def uses_python(project: Path) -> bool:
    """Return whether we detect a python project"""
    if any(project.glob("**/*.py")):
        logger.debug("*.py found, assuming we use python")
        return True
    return False


def uses_ansible(project: Path) -> bool:
    """Return whether we detect an ansible dir"""
    if (project / "ansible").exists():
        logger.debug("ansible/ dir found, assuming we use ansible")
        return True
    return False
