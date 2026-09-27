"""Unit tests for scripts/aipp_settings.py.

All tests use temp/fixture paths, never ~/.claude/.
"""

import json
from unittest.mock import patch

import aipp_settings as settings
import pytest


def test_load_returns_empty_projects_for_missing_file(tmp_path):
    target = tmp_path / "aipp-settings.json"
    assert settings.load(target) == {"projects": {}}


def test_load_creates_no_file_on_missing_path(tmp_path):
    target = tmp_path / "nested" / "aipp-settings.json"
    settings.load(target)
    assert not target.exists()


def test_load_raises_on_malformed_json(tmp_path):
    target = tmp_path / "aipp-settings.json"
    target.write_text("{not valid json")
    with pytest.raises(json.JSONDecodeError):
        settings.load(target)


def test_save_creates_parent_dir_if_absent(tmp_path):
    target = tmp_path / "sub" / "dir" / "aipp-settings.json"
    settings.save({"projects": {}}, target)
    assert target.exists()
    assert json.loads(target.read_text()) == {"projects": {}}


def test_save_writes_atomically_via_tempfile_and_replace(tmp_path):
    target = tmp_path / "aipp-settings.json"
    with patch("os.replace") as mock_replace:
        settings.save({"projects": {"x": {}}}, target)
        assert mock_replace.called
        tmp_arg = mock_replace.call_args[0][0]
        assert str(tmp_arg).endswith(".tmp")
    # os.replace was mocked out, so the final path must NOT exist (no partial/final file
    # left behind if the replace step is interrupted) -- only the temp file does.
    assert not target.exists()


def test_save_no_partial_file_survives_a_real_roundtrip(tmp_path):
    target = tmp_path / "aipp-settings.json"
    settings.save({"projects": {"a": {"skills": {"x": True}}}}, target)
    tmp_file = target.with_suffix(target.suffix + ".tmp")
    assert not tmp_file.exists()
    assert target.exists()


def test_get_project_returns_default_shape_for_unknown_path(tmp_path):
    target = tmp_path / "aipp-settings.json"
    settings.save({"projects": {}}, target)
    entry = settings.get_project("/some/project", target)
    assert entry == {"skills": {}, "agents": {}, "instructions": {}}


def test_get_project_does_not_mutate_other_projects_on_disk(tmp_path):
    target = tmp_path / "aipp-settings.json"
    other = {"skills": {"a": True}, "agents": {}, "instructions": {}}
    settings.save({"projects": {"/other": other}}, target)
    settings.get_project("/new/project", target)
    data = settings.load(target)
    assert data["projects"]["/other"] == {
        "skills": {"a": True},
        "agents": {},
        "instructions": {},
    }
    assert "/new/project" not in data["projects"]


def test_get_project_fills_missing_category_keys(tmp_path):
    target = tmp_path / "aipp-settings.json"
    settings.save({"projects": {"/p": {"skills": {"a": True}}}}, target)
    entry = settings.get_project("/p", target)
    assert entry == {"skills": {"a": True}, "agents": {}, "instructions": {}}


def _write_legacy(project_dir, filename, lines):
    (project_dir / filename).write_text("\n".join(lines) + "\n" if lines else "")


def test_migrate_legacy_files_produces_correct_true_false_entries(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()
    _write_legacy(project, ".skillsignore", ["# enabled-skill", "disabled-skill"])
    _write_legacy(project, ".agentsignore", ["#### Section ####", "# enabled-agent"])
    _write_legacy(project, ".rulesignore", ["disabled-rule"])

    result = settings.migrate_legacy_files(str(project), target)

    assert result is True
    data = settings.load(target)
    entry = data["projects"][str(project)]
    assert entry["skills"] == {"enabled-skill": True, "disabled-skill": False}
    assert entry["agents"] == {"enabled-agent": True}
    assert entry["instructions"] == {"disabled-rule": False}


def test_migrate_legacy_files_deletes_legacy_files_on_success(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()
    _write_legacy(project, ".skillsignore", ["# a"])
    _write_legacy(project, ".agentsignore", ["b"])
    _write_legacy(project, ".rulesignore", ["# c"])

    settings.migrate_legacy_files(str(project), target)

    assert not (project / ".skillsignore").exists()
    assert not (project / ".agentsignore").exists()
    assert not (project / ".rulesignore").exists()


def test_migrate_legacy_files_is_noop_when_entry_already_exists(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()
    existing = {"skills": {"x": True}, "agents": {}, "instructions": {}}
    settings.save({"projects": {str(project): existing}}, target)
    _write_legacy(project, ".skillsignore", ["# should-not-be-read"])

    result = settings.migrate_legacy_files(str(project), target)

    assert result is False
    data = settings.load(target)
    assert data["projects"][str(project)] == existing
    assert (project / ".skillsignore").exists()


def test_migrate_legacy_files_noop_when_no_legacy_files_exist(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()

    result = settings.migrate_legacy_files(str(project), target)

    assert result is False
    data = settings.load(target)
    assert str(project) not in data.get("projects", {})


def test_migrate_legacy_files_empty_file_produces_empty_dict_not_skip(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()
    _write_legacy(project, ".skillsignore", [])

    result = settings.migrate_legacy_files(str(project), target)

    assert result is True
    data = settings.load(target)
    entry = data["projects"][str(project)]
    assert entry == {"skills": {}, "agents": {}, "instructions": {}}


def test_migrate_legacy_files_skips_blank_and_section_header_lines(tmp_path):
    target = tmp_path / "aipp-settings.json"
    project = tmp_path / "proj"
    project.mkdir()
    _write_legacy(
        project,
        ".skillsignore",
        ["#### My Section ####", "", "# real-item", ""],
    )

    settings.migrate_legacy_files(str(project), target)

    data = settings.load(target)
    entry = data["projects"][str(project)]
    assert entry["skills"] == {"real-item": True}
