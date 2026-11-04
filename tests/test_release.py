import json
from pathlib import Path

import polars as pl
import pytest

from lobbynet_analysis.release import (
    ReleaseError,
    ReleaseLock,
    connect,
    fetch_release,
    sha256_file,
)


def _release(root: Path, version: str = "v0.1", schema: str = "1.0") -> str:
    """Write a tiny release like the pipeline does; return the manifest checksum."""
    folder = root / version
    folder.mkdir(parents=True)
    pl.DataFrame({"edge_id": ["e1", "e2"]}).write_parquet(folder / "edge.parquet")
    manifest = {
        "title": "t",
        "data_version": version,
        "schema_version": schema,
        "files": [
            {
                "table": "edge",
                "file": "edge.parquet",
                "rows": 2,
                "sha256": sha256_file(folder / "edge.parquet"),
            }
        ],
    }
    (folder / "manifest.json").write_text(json.dumps(manifest))
    return sha256_file(folder / "manifest.json")


def test_fetch_copies_verifies_and_opens(tmp_path: Path) -> None:
    source = tmp_path / "pipeline"
    lock = ReleaseLock("v0.1", 1, _release(source), source)

    target = fetch_release(lock, tmp_path / "local")

    assert target == tmp_path / "local" / "v0.1"
    assert connect(target).execute("SELECT count(*) FROM edge").fetchone() == (2,)
    # a second fetch keeps the verified copy
    assert fetch_release(lock, tmp_path / "local") == target


def test_altered_table_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "pipeline"
    lock = ReleaseLock("v0.1", 1, _release(source), source)
    pl.DataFrame({"edge_id": ["changed"]}).write_parquet(source / "v0.1" / "edge.parquet")

    with pytest.raises(ReleaseError, match="differs from its manifest"):
        fetch_release(lock, tmp_path / "local")
    assert not (tmp_path / "local" / "v0.1").exists()


def test_other_manifest_or_schema_major_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "pipeline"
    checksum = _release(source, schema="2.0")

    with pytest.raises(ReleaseError, match="not the pinned manifest"):
        fetch_release(ReleaseLock("v0.1", 2, "0" * 64, source), tmp_path / "a")
    with pytest.raises(ReleaseError, match="breaking change"):
        fetch_release(ReleaseLock("v0.1", 1, checksum, source), tmp_path / "b")
