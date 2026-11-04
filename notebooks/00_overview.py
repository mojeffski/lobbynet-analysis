import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from lobbynet_analysis.release import connect, load_lock

    return connect, load_lock, mo


@app.cell
def _(mo):
    mo.md(r"""
    # 00 – Erster Blick auf das Release

    Dieses Notebook ist der Einstieg: Es öffnet das festgelegte Release
    (`config/release.yaml`) und stellt eine einzige Frage —
    **wie groß ist das Netzwerk in jedem Snapshot?**

    So funktioniert marimo:
    - Jede Zelle ist Python. Ändert sich eine Zelle, laufen alle Zellen,
      die von ihr abhängen, automatisch neu.
    - Ein Name (z. B. `con`) darf nur in **einer** Zelle definiert werden.
    - Starten: `uv run marimo edit notebooks/00_overview.py`

    Lesehinweise zu den Daten: `data/releases/v0.1/README.md` und
    `docs/data_notes.md`.
    """)
    return


@app.cell
def _(connect, load_lock):
    lock = load_lock()
    con = connect()  # DuckDB with one view per table: snapshot, edge, ...
    lock.data_version
    return (con,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Die Snapshots

    Die Zeit ist der Snapshot, nicht ein Datum. Die Abstände sind
    ungleich (2018 fehlt ganz) — deshalb `months_since_previous`.
    """)
    return


@app.cell
def _(con):
    con.sql(
        """
        SELECT snapshot_index, snapshot_label, months_since_previous,
               schema_era, n_registered
        FROM snapshot
        ORDER BY snapshot_index
        """
    ).pl()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Kanten pro Snapshot

    `edge_snapshot` hat eine Zeile pro Kante und Snapshot.
    - `observed`: Die Mitgliedschaft wurde in diesem Snapshot berichtet.
    - `observable`: Sie *hätte* berichtet werden können (eine Seite
      registriert und ihr Feld ausgefüllt). `observed = false` mit
      `observable = false` heißt **unbekannt**, nicht „beendet“.
    """)
    return


@app.cell
def _(con):
    edges_per_snapshot = con.sql(
        """
        SELECT snapshot_label,
               count(*) FILTER (WHERE observed)   AS observed,
               count(*) FILTER (WHERE observable) AS observable
        FROM edge_snapshot
        GROUP BY snapshot_label
        ORDER BY snapshot_label
        """
    ).pl()
    edges_per_snapshot
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Zum Weitermachen (gemeinsam)

    1. Wie verändert sich das Verhältnis `observed / n_registered` über
       die Zeit? Was könnte die Sprünge erklären (Schema-Ära!)?
    2. Wie viele Kanten haben nur registrierte Knoten an beiden Enden?
       (Tipp: `edge` mit `organisation` verbinden, `is_registered`)
    3. Welche Organisationen haben im letzten Snapshot die meisten
       Mitglieder — und welche davon sind wirklich Verbände?
       (Dopper-Befund in `docs/data_notes.md`)
    """)
    return


if __name__ == "__main__":
    app.run()
