#!/usr/bin/env python3
"""Deep-merge a repo config into a local one (lodash-style), write result to dest.

Usage: merge_config.py <repo_config> <local_config> <dest>
"""

import json
import logging
from pathlib import Path
import sys

import yaml

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

Scalar = str | int | float | bool | None
JSONValue = dict[str, "JSONValue"] | list["JSONValue"] | Scalar


def merge(repo: JSONValue, local: JSONValue) -> JSONValue:
    """Deep-merge `repo` into `local`, lodash `_.merge` style.

    Args:
        repo: Value from the repo config (wins on scalar conflict).
        local: Value from the local config.

    Returns:
        The merged value: dicts merge recursively, lists concatenate and
        dedupe (repo items first), scalars take the repo value.
    """
    if isinstance(repo, dict) and isinstance(local, dict):
        merged_dict: dict[str, JSONValue] = dict(local)
        for key, value in repo.items():
            merged_dict[key] = merge(value, local[key]) if key in local else value
        return merged_dict
    if isinstance(repo, list) and isinstance(local, list):
        seen: set[Scalar] = set()
        merged_list: list[JSONValue] = []
        for item in repo + local:
            dedup_key: Scalar
            if isinstance(item, (dict, list)):
                dedup_key = json.dumps(item, sort_keys=True)
            else:
                dedup_key = item
            if dedup_key not in seen:
                seen.add(dedup_key)
                merged_list.append(item)
        return merged_list
    # why: lodash _.merge semantics — later (repo) source wins on scalar conflict
    return repo


def load(path: Path) -> JSONValue:
    """Load a JSON or YAML config file.

    Args:
        path: Path to the config file; format inferred from its extension.

    Returns:
        The parsed config, or `{}` if the file is empty.
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    return json.loads(text) if text.strip() else {}


def dump(data: JSONValue, path: Path) -> None:
    """Write `data` to `path` as JSON or YAML, per its extension.

    Args:
        data: The config data to serialize.
        path: Destination path; format inferred from its extension.
    """
    if path.suffix in (".yaml", ".yml"):
        text = yaml.dump(
            data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        path.write_text(text, encoding="utf-8")
    else:
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")


def main() -> None:
    """Merge `repo_config` into `local_config` (if present) and write `dest`."""
    if len(sys.argv) != 4:
        logger.error("Usage: merge_config.py <repo_config> <local_config> <dest>")
        sys.exit(1)

    repo_path, local_path, dest_path = (Path(p) for p in sys.argv[1:4])

    repo_data = load(repo_path)
    if local_path.exists() and not local_path.is_symlink():
        local_data = load(local_path)
        result = merge(repo_data, local_data)
    else:
        result = repo_data

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dump(result, dest_path)
    logger.info("Merged -> %s", dest_path)


if __name__ == "__main__":
    main()
