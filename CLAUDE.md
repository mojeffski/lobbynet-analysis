# CLAUDE.md – lobbynet-analysis

Projekt **P1 Datenanalyse** im lobbynet-Vorhaben. Lies zu Beginn jeder Sitzung:

1. diese Datei
2. die **Projektlandkarte** `/Users/weemoe/Documents/Projects/Lobbynet/docs/projects.md`
   (alle Projekte, Releases, Entscheidungen, nächste Schritte); führe sie
   nach, wenn sich hier etwas Wesentliches ändert
3. das README des genutzten Releases `data/releases/<version>/README.md`
   (Lesehinweise, Zeitsemantik, ab v0.2 „Known limitations“) und
   `docs/data_notes.md`

## Worum es geht

Analyse der historischen, gerichteten Netzwerke von Mitgliedschaften zwischen
Organisationen aus dem EU-Transparenzregister (2015–2026), die die Pipeline
`lobbynet` als versionierte Releases erzeugt. Forschungsrahmen:
Interessenvertretung, Machtasymmetrien, EU-Integration; (historische)
Netzwerkanalyse; kritische politische Ökonomie. Die Forschungsfragen
entstehen aus dem Literaturreview des Projektinhabers (P4).

## Arbeitsweise: Hand in Hand

**Der Projektinhaber will selbst lernen, die Daten zu analysieren.** Claude
liefert deshalb keine fertigen Analysen ab, sondern:
- erklärt Konzepte und Methoden (Netzwerkkennzahlen, Zeitsemantik, Statistik)
- schlägt den nächsten Schritt vor und baut ihn **gemeinsam** auf, in kleinen
  Schritten, die er selbst nachvollziehen und verändern kann
- lässt Lücken zum Selbermachen („Zum Weitermachen“ in den Notebooks) und
  prüft dann gemeinsam das Ergebnis
- schreibt Infrastruktur (Laden, Exporte, Hilfsfunktionen) selbst, mit Tests

Erst planen, dann bauen; neue Abhängigkeiten nur nach Rückfrage, mit einer
Zeile Begründung. Erklärungen auf Deutsch.

## Regeln

- **Nur Releases lesen, nie Zwischenstände der Pipeline** (ADR-0011 der
  Pipeline). Das genutzte Release steht in `config/release.yaml` und wird mit
  `uv run lobbynet-analysis fetch` geholt und gegen das Manifest geprüft.
- **Ein Release wird nie verändert.** Abgeleitetes kommt nach
  `outputs/<version>/` (`lobbynet_analysis.release.outputs_dir`), damit ein
  Wechsel der Version alte Ergebnisse nicht überschreibt.
- **Datenfehler werden nicht hier repariert**, sondern als Befund in der
  Pipeline vermerkt (`Lobbynet/docs/plan/umsetzungsplan.md`) und dort für das
  nächste Release behoben. Hier höchstens dokumentierte Filter.
- **Fehlend ist nicht 0:** Zeitreihen über `edge_snapshot.observable` lesen;
  Snapshots sind ungleich verteilt (2018 fehlt).
- Wiederverwendbare Logik liegt in `src/lobbynet_analysis/` (Funktionen mit
  Typannotationen und Docstring im NumPy-Stil, Tests). Notebooks sind dünn.

## Sprache

Code, Bezeichner, Docstrings, Commit-Messages: Englisch. Notebook-Erklärungen,
Notizen und Pläne: Deutsch.

## Kommandos

| Zweck | Kommando |
| --- | --- |
| Release holen und prüfen | `uv run lobbynet-analysis fetch` |
| Inhalt des Releases anzeigen | `uv run lobbynet-analysis info` |
| Notebook bearbeiten | `uv run marimo edit notebooks/00_overview.py` |
| Notebook als Skript laufen lassen | `uv run python notebooks/00_overview.py` |
| DuckDB-UI (Views: `.read sql/setup.sql`) | `duckdb -ui` aus diesem Ordner |
| Tests | `uv run pytest` |
| Lint und Format | `uv run ruff check .` und `uv run ruff format --check .` |
| Typprüfung | `uv run pyright` |
| Hooks einmalig installieren | `uv run pre-commit install` |

## Struktur

| Ordner | Inhalt |
| --- | --- |
| `config/` | `release.yaml`: genutzte Version, Schema-Hauptversion, Prüfsumme |
| `src/lobbynet_analysis/` | Laden des Releases, später Exporte (GEXF) und Hilfsfunktionen |
| `notebooks/` | marimo-Notebooks, nummeriert |
| `sql/` | DuckDB-Abfragen |
| `r/` | R-Skripte, erst bei Bedarf (Pakete mit `renv`) |
| `docs/` | Datennotizen, Analysenotizen |
| `data/`, `outputs/` | geholte Releases und Ergebnisse, nicht in git |
