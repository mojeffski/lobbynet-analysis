"""Fetch, verify and open a lobbynet data release.

A release is an immutable folder written by the pipeline (`lobbynet`,
ADR-0011): Parquet tables, `manifest.json` with a SHA-256 per table, README,
data dictionary and changelog. This project never reads pipeline
intermediates and never changes a release. It pins one version in
`config/release.yaml`, copies that folder into `data/releases/<version>/`
and checks every table against the manifest.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import yaml

ROOT = Path(__file__).resolve().parents[2]
"""Repository root; relative paths in the configuration start here."""


class ReleaseError(Exception):
    """Raised when a release is missing, altered or of an incompatible schema."""


@dataclass(frozen=True)
class ReleaseLock:
    """The pinned release, from `config/release.yaml`.

    Attributes
    ----------
    data_version : str
        Release version, e.g. ``"v0.1"``.
    schema_major : int
        Major schema version the analyses are written for. A release with
        another major version is refused (breaking change).
    manifest_sha256 : str
        Checksum of the release's `manifest.json`; pins the exact content.
    source : Path
        Folder holding the pipeline's releases (one subfolder per version).
    """

    data_version: str
    schema_major: int
    manifest_sha256: str
    source: Path


def load_lock(path: Path = ROOT / "config" / "release.yaml") -> ReleaseLock:
    """Read the pinned release from the configuration.

    Parameters
    ----------
    path : Path
        The configuration file.

    Returns
    -------
    ReleaseLock
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    source = Path(raw["source"])
    return ReleaseLock(
        data_version=raw["data_version"],
        schema_major=int(raw["schema_major"]),
        manifest_sha256=raw["manifest_sha256"],
        source=source if source.is_absolute() else (path.parent.parent / source).resolve(),
    )


def sha256_file(path: Path) -> str:
    """SHA-256 of a file, read in chunks.

    Parameters
    ----------
    path : Path
        The file.

    Returns
    -------
    str
        Hex digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(release_dir: Path) -> dict[str, Any]:
    """Read `manifest.json` of a release folder.

    Parameters
    ----------
    release_dir : Path
        The release folder.

    Returns
    -------
    dict[str, Any]
    """
    return json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))


def verify_release(release_dir: Path, lock: ReleaseLock) -> dict[str, Any]:
    """Check a release folder against the lock and its own manifest.

    Parameters
    ----------
    release_dir : Path
        The release folder.
    lock : ReleaseLock
        The pinned release.

    Returns
    -------
    dict[str, Any]
        The manifest.

    Raises
    ------
    ReleaseError
        If the manifest is missing or not the pinned one, the schema major
        version differs, or a table is missing or altered.
    """
    manifest_path = release_dir / "manifest.json"
    if not manifest_path.exists():
        raise ReleaseError(f"No manifest in {release_dir}")
    if sha256_file(manifest_path) != lock.manifest_sha256:
        raise ReleaseError(
            f"{manifest_path} is not the pinned manifest; update manifest_sha256 in "
            "config/release.yaml only on purpose (new release)"
        )
    manifest = read_manifest(release_dir)
    major = int(str(manifest["schema_version"]).split(".")[0])
    if major != lock.schema_major:
        raise ReleaseError(
            f"Release {manifest['data_version']} has schema {manifest['schema_version']}, "
            f"the analyses are written for {lock.schema_major}.x: breaking change, adapt "
            "the code before switching"
        )
    for entry in manifest["files"]:
        path = release_dir / entry["file"]
        if not path.exists():
            raise ReleaseError(f"Missing table file {path}")
        if sha256_file(path) != entry["sha256"]:
            raise ReleaseError(f"{path} differs from its manifest checksum")
    return manifest


def fetch_release(lock: ReleaseLock, target_root: Path = ROOT / "data" / "releases") -> Path:
    """Copy the pinned release into this project and verify it.

    An already fetched, intact copy is left as it is. The copy is assembled
    under a temporary name and renamed only after verification, so a broken
    copy never looks like a release.

    Parameters
    ----------
    lock : ReleaseLock
        The pinned release.
    target_root : Path
        Folder for local releases.

    Returns
    -------
    Path
        The local release folder.

    Raises
    ------
    ReleaseError
        If the source is missing or fails verification.
    """
    target = target_root / lock.data_version
    if target.exists():
        verify_release(target, lock)
        return target
    source = lock.source / lock.data_version
    if not source.exists():
        raise ReleaseError(f"Release {lock.data_version} not found in {lock.source}")
    staging = target_root / f".{lock.data_version}.partial"
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(source, staging)
    try:
        verify_release(staging, lock)
    except ReleaseError:
        shutil.rmtree(staging)
        raise
    staging.rename(target)
    return target


def release_dir(lock: ReleaseLock | None = None) -> Path:
    """Folder of the pinned, fetched release.

    Parameters
    ----------
    lock : ReleaseLock | None
        The pinned release; `None` reads `config/release.yaml`.

    Returns
    -------
    Path

    Raises
    ------
    ReleaseError
        If the release has not been fetched yet.
    """
    lock = lock or load_lock()
    path = ROOT / "data" / "releases" / lock.data_version
    if not path.exists():
        raise ReleaseError(
            f"Release {lock.data_version} not fetched: uv run lobbynet-analysis fetch"
        )
    return path


def connect(path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB with one view per release table.

    Parameters
    ----------
    path : Path | None
        Release folder; `None` uses the pinned, fetched release.

    Returns
    -------
    duckdb.DuckDBPyConnection
        Views named like the tables (`organisation`, `edge`, …).

    Examples
    --------
    >>> con = connect()  # doctest: +SKIP
    >>> con.sql("SELECT count(*) FROM edge").pl()  # doctest: +SKIP
    """
    path = path or release_dir()
    con = duckdb.connect()
    for entry in read_manifest(path)["files"]:
        file = (path / entry["file"]).as_posix().replace("'", "''")
        con.execute(f"CREATE VIEW {entry['table']} AS SELECT * FROM read_parquet('{file}')")
    return con


def outputs_dir(data_version: str | None = None) -> Path:
    """Folder for results computed from one release version.

    Results are kept per version, so that switching to a new release never
    overwrites the results of the old one.

    Parameters
    ----------
    data_version : str | None
        Release version; `None` uses the pinned one.

    Returns
    -------
    Path
        `outputs/<version>/`, created if missing.
    """
    out = ROOT / "outputs" / (data_version or load_lock().data_version)
    out.mkdir(parents=True, exist_ok=True)
    return out
