#!/usr/bin/env python3
"""Verify the catalog offline. Python 3.11+ and a BLAKE3 command are required."""
import argparse
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib


def member(root, name):
    path = root / name
    if Path(name).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes catalog: {name}")
    if not path.is_file():
        raise ValueError(f"missing catalog file: {name}")
    return path


def digest(path, hasher):
    result = subprocess.check_output([*hasher, str(path)], text=True).split()
    if not result or not re.fullmatch(r"[0-9a-f]{64}", result[0]):
        raise ValueError(f"invalid hasher output for {path}")
    return result[0]


def verify(root, hasher):
    catalog = tomllib.loads((root / "manifest.toml").read_text())
    if catalog.get("schema") != 1 or not catalog.get("firmware"):
        raise ValueError("unsupported or empty firmware catalog")
    paths = set()
    for name, entry in catalog["licenses"].items():
        if digest(member(root, entry["file"]), hasher) != entry["blake3"]:
            raise ValueError(f"license digest mismatch: {name}")
    for name, entry in catalog["firmware"].items():
        path = member(root, entry["file"])
        if entry["file"] in paths:
            raise ValueError(f"duplicate firmware file: {path}")
        paths.add(entry["file"])
        if not entry.get("vendor") or not entry.get("family"):
            raise ValueError(f"missing vendor/family: {name}")
        if not re.fullmatch(r"[^@]+@[0-9a-f]{40}:.+", entry["source"]):
            raise ValueError(f"source must pin a full commit: {name}")
        if entry["license"] not in catalog["licenses"]:
            raise ValueError(f"missing license mapping: {name}")
        if path.stat().st_size != entry["size"] or digest(path, hasher) != entry["blake3"]:
            raise ValueError(f"firmware size or digest mismatch: {name}")
    print(f"firmware: verified {len(paths)} blobs and {len(catalog['licenses'])} license notices")
    return catalog


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hasher", default="b3sum", help="BLAKE3 command, e.g. 'cargo run -q -p kore-b3sum --'")
    args = parser.parse_args()
    try:
        verify(Path(__file__).resolve().parent, shlex.split(args.hasher))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(f"firmware: FAIL: {error}")
