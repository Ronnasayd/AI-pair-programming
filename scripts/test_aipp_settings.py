"""Unit tests for scripts/aipp_settings.py.

All tests use temp/fixture paths, never ~/.claude/.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import aipp_settings as settings
import pytest
import yaml

SCRIPT_PATH = Path(__file__).parent / "aipp_settings.py"


def _run_cli(args, home_dir):
    """Run the CLI with HOME redirected to home_dir, so SETTINGS_PATH (~/.claude/...)
    never touches the real user config."""
    env = {**os.environ, "HOME": str(home_dir)}
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


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


def _write_default_settings(source_dir, skills=None, agents=None, instructions=None):
    catalog_dir = source_dir / "claude"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "skills": skills or {},
        "agents": agents or {},
        "instructions": instructions or {},
    }
    (catalog_dir / "aipp-default-settings.json").write_text(json.dumps(data))


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


def test_seed_from_source_defaults_new_project_matches_default_settings_json(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    local = tmp_path / "local"
    local.mkdir()
    _write_default_settings(
        source,
        skills={"enabled-skill": True, "disabled-skill": False},
        agents={"enabled-agent": True},
        instructions={"disabled-rule": False},
    )

    settings.seed_from_source_defaults(str(local), str(source), target)

    entry = settings.load(target)["projects"][str(local)]
    assert entry["skills"] == {"enabled-skill": True, "disabled-skill": False}
    assert entry["agents"] == {"enabled-agent": True}
    assert entry["instructions"] == {"disabled-rule": False}


def test_ensure_migrated_does_not_reseed_already_migrated_project(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    local = tmp_path / "local"
    local.mkdir()
    _write_default_settings(source, skills={"source-item": True})
    existing = {"skills": {"local-item": False}, "agents": {}, "instructions": {}}
    settings.save({"projects": {str(local): existing}}, target)

    settings.ensure_migrated(str(local), str(source), target)

    entry = settings.load(target)["projects"][str(local)]
    # why: migrate no-ops since entry pre-existed, value must survive seeding
    assert entry["skills"]["local-item"] is False


def test_seed_never_overwrites_existing_key_present_in_both(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    local = tmp_path / "local"
    local.mkdir()
    _write_default_settings(source, skills={"shared-item": True})
    existing = {"skills": {"shared-item": False}, "agents": {}, "instructions": {}}
    settings.save({"projects": {str(local): existing}}, target)

    settings.seed_from_source_defaults(str(local), str(source), target)

    entry = settings.load(target)["projects"][str(local)]
    assert entry["skills"]["shared-item"] is False


def test_ensure_migrated_migrates_then_seeds_missing_items(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    local = tmp_path / "local"
    local.mkdir()
    _write_legacy(local, ".skillsignore", ["# local-item"])
    _write_default_settings(source, skills={"source-item": True, "local-item": False})

    settings.ensure_migrated(str(local), str(source), target)

    entry = settings.load(target)["projects"][str(local)]
    assert entry["skills"]["local-item"] is True
    assert entry["skills"]["source-item"] is True
    assert not (local / ".skillsignore").exists()


def test_register_if_absent_adds_new_key_with_default(tmp_path):
    target = tmp_path / "aipp-settings.json"
    settings.register_if_absent("/proj", "skills", "new-skill", False, target)

    entry = settings.load(target)["projects"]["/proj"]
    assert entry["skills"] == {"new-skill": False}


def test_register_if_absent_noop_when_key_already_present(tmp_path):
    target = tmp_path / "aipp-settings.json"
    existing = {"skills": {"x": True}, "agents": {}, "instructions": {}}
    settings.save({"projects": {"/proj": existing}}, target)

    settings.register_if_absent("/proj", "skills", "x", False, target)

    entry = settings.load(target)["projects"]["/proj"]
    assert entry["skills"]["x"] is True


def test_set_item_creates_project_and_category_if_missing(tmp_path):
    target = tmp_path / "aipp-settings.json"
    settings.set_item("/proj", "agents", "my-agent", True, target)

    entry = settings.load(target)["projects"]["/proj"]
    assert entry["agents"] == {"my-agent": True}


def test_set_item_overwrites_existing_value(tmp_path):
    target = tmp_path / "aipp-settings.json"
    existing = {"skills": {"x": False}, "agents": {}, "instructions": {}}
    settings.save({"projects": {"/proj": existing}}, target)

    settings.set_item("/proj", "skills", "x", True, target)

    entry = settings.load(target)["projects"]["/proj"]
    assert entry["skills"]["x"] is True


def test_cli_ensure_migrated_runs_and_exits_zero(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    source = tmp_path / "source"
    source.mkdir()
    local = tmp_path / "local"
    local.mkdir()
    _write_default_settings(source, skills={"source-item": True})

    result = _run_cli(["ensure-migrated", str(local), str(source)], home)

    assert result.returncode == 0
    settings_file = home / ".claude" / "aipp-settings.json"
    data = json.loads(settings_file.read_text())
    assert data["projects"][str(local)]["skills"] == {"source-item": True}


def test_cli_register_if_absent_adds_key_when_absent_and_exits_zero(tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    result = _run_cli(
        ["register-if-absent", "/some/project", "skills", "my-skill", "false"], home
    )

    assert result.returncode == 0
    settings_file = home / ".claude" / "aipp-settings.json"
    data = json.loads(settings_file.read_text())
    assert data["projects"]["/some/project"]["skills"] == {"my-skill": False}


def test_cli_exits_nonzero_with_stderr_on_malformed_json(tmp_path):
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "aipp-settings.json").write_text("{not valid json")

    result = _run_cli(
        ["register-if-absent", "/some/project", "skills", "my-skill", "false"], home
    )

    assert result.returncode != 0
    assert "error" in result.stderr.lower()


def _write_index_yaml(source_dir, category, names):
    index_dir = source_dir / _INDEX_YAML_DIR[category]
    index_dir.mkdir(parents=True, exist_ok=True)
    entries = [{"name": [name], "description": "desc"} for name in names]
    (index_dir / "index.yaml").write_text(yaml.dump({category: entries}))


_INDEX_YAML_DIR = {
    "skills": "skills",
    "agents": "agents",
    "instructions": "instructions",
}


def test_sync_catalog_adds_new_item_to_catalog_file(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    _write_default_settings(source, skills={"old-skill": True})
    _write_index_yaml(source, "skills", ["old-skill", "new-skill"])

    settings.sync_catalog(str(source), target)

    catalog = json.loads((source / "claude" / "aipp-default-settings.json").read_text())
    assert catalog["skills"] == {"old-skill": True, "new-skill": False}


def test_sync_catalog_propagates_new_item_to_existing_projects(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    _write_default_settings(source)
    _write_index_yaml(source, "agents", ["new-agent.agent.md"])
    proj_a = str(tmp_path / "proj_a")
    proj_b = str(tmp_path / "proj_b")
    settings.save(
        {
            "projects": {
                proj_a: {"skills": {}, "agents": {}, "instructions": {}},
                proj_b: {"skills": {}, "agents": {"other": True}, "instructions": {}},
            }
        },
        target,
    )

    settings.sync_catalog(str(source), target)

    data = settings.load(target)
    assert data["projects"][proj_a]["agents"] == {"new-agent.agent.md": False}
    assert data["projects"][proj_b]["agents"] == {
        "other": True,
        "new-agent.agent.md": False,
    }


def test_sync_catalog_never_overwrites_existing_catalog_value(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    _write_default_settings(source, skills={"enabled-skill": True})
    _write_index_yaml(source, "skills", ["enabled-skill"])

    settings.sync_catalog(str(source), target)

    catalog = json.loads((source / "claude" / "aipp-default-settings.json").read_text())
    assert catalog["skills"]["enabled-skill"] is True


def test_sync_catalog_registers_already_catalogued_item_on_new_project(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    # why: reproduces the pre-fix bug -- "new_names" excluded items already in
    # the catalog, so a project migrated before this item existed never got it
    _write_default_settings(source, skills={"old-catalogued-skill": False})
    _write_index_yaml(source, "skills", ["old-catalogued-skill"])
    proj = str(tmp_path / "proj")
    settings.save(
        {"projects": {proj: {"skills": {}, "agents": {}, "instructions": {}}}},
        target,
    )

    settings.sync_catalog(str(source), target)

    data = settings.load(target)
    assert data["projects"][proj]["skills"] == {"old-catalogued-skill": False}


def test_sync_catalog_skips_items_already_present_per_project(tmp_path):
    target = tmp_path / "aipp-settings.json"
    source = tmp_path / "source"
    source.mkdir()
    _write_default_settings(source)
    _write_index_yaml(source, "instructions", ["shared.instructions.md"])
    proj = str(tmp_path / "proj")
    settings.save(
        {
            "projects": {
                proj: {
                    "skills": {},
                    "agents": {},
                    "instructions": {"shared.instructions.md": True},
                }
            }
        },
        target,
    )

    settings.sync_catalog(str(source), target)

    data = settings.load(target)
    assert data["projects"][proj]["instructions"]["shared.instructions.md"] is True


def test_cli_sync_catalog_runs_and_exits_zero(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    source = tmp_path / "source"
    source.mkdir()
    _write_default_settings(source)
    _write_index_yaml(source, "skills", ["fresh-skill"])

    result = _run_cli(["sync-catalog", str(source)], home)

    assert result.returncode == 0
    catalog = json.loads((source / "claude" / "aipp-default-settings.json").read_text())
    assert catalog["skills"] == {"fresh-skill": False}
