-- Views on the pinned, fetched release (config/release.yaml).
-- In `duckdb -ui` started from this repository: paste into a notebook cell
-- or run `.read sql/setup.sql`. Change the version in one place below.
-- Read-only: nothing is written.
SET VARIABLE release = 'data/releases/v0.1.1/';

CREATE OR REPLACE VIEW snapshot AS SELECT * FROM read_parquet(getvariable('release') || 'snapshot.parquet');
CREATE OR REPLACE VIEW organisation AS SELECT * FROM read_parquet(getvariable('release') || 'organisation.parquet');
CREATE OR REPLACE VIEW organisation_snapshot AS SELECT * FROM read_parquet(getvariable('release') || 'organisation_snapshot.parquet');
CREATE OR REPLACE VIEW report_status AS SELECT * FROM read_parquet(getvariable('release') || 'report_status.parquet');
CREATE OR REPLACE VIEW observation AS SELECT * FROM read_parquet(getvariable('release') || 'observation.parquet');
CREATE OR REPLACE VIEW edge AS SELECT * FROM read_parquet(getvariable('release') || 'edge.parquet');
CREATE OR REPLACE VIEW edge_snapshot AS SELECT * FROM read_parquet(getvariable('release') || 'edge_snapshot.parquet');
CREATE OR REPLACE VIEW id_history AS SELECT * FROM read_parquet(getvariable('release') || 'id_history.parquet');
-- since v0.1.1 (schema 1.1): full texts and all extracted mentions
CREATE OR REPLACE VIEW text AS SELECT * FROM read_parquet(getvariable('release') || 'text.parquet');
CREATE OR REPLACE VIEW mention AS SELECT * FROM read_parquet(getvariable('release') || 'mention.parquet');
