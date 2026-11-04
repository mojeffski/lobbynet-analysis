# lobbynet-analysis

Analysis of the lobbynet data releases: historical, directed networks of
memberships between organisations in the EU Transparency Register
(2015–2026). Reads only versioned releases of the `lobbynet` pipeline.

```bash
uv sync
uv run lobbynet-analysis fetch          # copy and verify the pinned release
uv run marimo edit notebooks/00_overview.py
```

Context and rules: `CLAUDE.md`. Data caveats: `docs/data_notes.md`.
