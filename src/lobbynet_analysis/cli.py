"""Command line: `uv run lobbynet-analysis fetch | info`."""

from __future__ import annotations

import argparse

from lobbynet_analysis.release import ReleaseError, fetch_release, load_lock, read_manifest


def main(argv: list[str] | None = None) -> int:
    """Fetch the pinned release or show what it contains.

    Parameters
    ----------
    argv : list[str] | None
        Arguments; `None` reads `sys.argv`.

    Returns
    -------
    int
        Exit code (0 on success, 1 on a release error).
    """
    parser = argparse.ArgumentParser(prog="lobbynet-analysis")
    parser.add_argument("command", choices=["fetch", "info"])
    args = parser.parse_args(argv)
    lock = load_lock()
    try:
        path = fetch_release(lock)
    except ReleaseError as error:
        print(f"Release error: {error}")
        return 1
    if args.command == "fetch":
        print(f"Release {lock.data_version} verified: {path}")
        return 0
    manifest = read_manifest(path)
    print(f"{manifest['title']}\n{manifest['data_version']}, schema {manifest['schema_version']}")
    for entry in manifest["files"]:
        print(f"  {entry['table']:<22} {entry['rows']:>10,} rows")
    return 0
