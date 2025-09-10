from pathlib import Path

from pytest_mock.plugin import MockerFixture

from nens_meta import utils


def test_strip_whitespace():
    content = "Example\n    \ncontent  \nend\n\n\n"
    expected = "Example\n\ncontent\nend\n"
    assert utils.strip_whitespace(content) == expected


def test_extract_extra_lines1():
    # Empty content should be ok
    assert utils._extract_extra_lines("") == ""


def test_extract_extra_lines2():
    content = f"bla\n{utils.EXTRA_LINES_MARKER}reinout\n"
    assert utils._extract_extra_lines(content) == "reinout\n"


def test_write_if_changed1(tmp_path: Path):
    # Just write something to a new file. The extra lines marker will also be in there.
    f = tmp_path / "sample.txt"
    utils.write_if_changed(f, "test")
    assert f.exists()
    content = f.read_text()
    assert content.startswith("test")
    assert utils.EXTRA_LINES_MARKER in content


def test_write_if_changed2(tmp_path: Path):
    # Write something new to an existing file.
    f = tmp_path / "sample.txt"
    f.write_text("bla bla")
    utils.write_if_changed(f, "test")
    content = f.read_text()
    assert content.startswith("test")


def test_write_if_changed3(tmp_path: Path, mocker: MockerFixture):
    # Don't change an existing file if it is not needed.
    f = tmp_path / "sample.txt"
    f.write_text("test\n\n" + utils.EXTRA_LINES_MARKER)
    writer = mocker.spy(Path, "write_text")
    utils.write_if_changed(f, "test\n")
    writer.assert_not_called()


def test_write_if_changed4(tmp_path: Path):
    # Don't write something if the file should be left alone
    f = tmp_path / "sample.txt"
    f.write_text("bla bla\n# NENS_META_LEAVE_ALONE\n")
    utils.write_if_changed(f, "test")
    content = f.read_text()
    assert content.startswith("bla bla")
    assert (tmp_path / "sample.txt.suggestion").exists()


def test_uses_python1():
    # We ourselves are a python project.
    ourselves = Path(__file__).parent.parent.parent.parent
    assert utils.uses_python(ourselves)


def test_uses_python2(tmp_path: Path):
    # An empty dir is not a python project
    assert not utils.uses_python(tmp_path)


def test_uses_ansible1():
    # We ourselves have no ansible/ dir.
    ourselves = Path(__file__).parent.parent.parent.parent
    assert not utils.uses_ansible(ourselves)


def test_uses_ansible2(tmp_path: Path):
    (tmp_path / "ansible").mkdir()
    assert utils.uses_ansible(tmp_path)
