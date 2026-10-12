-- AgencyZoom hands out duplicate lead source names ("X" twice, "Arizona
-- Insurance Reports" and "...!" -- the 2026-10-06 snapshot), so the name is
-- not unique; the id is. SQLite cannot drop a constraint, so the table is
-- rebuilt without it (nothing references lead_sources by name).
CREATE TABLE IF NOT EXISTS lead_sources_v2 (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);
INSERT OR IGNORE INTO lead_sources_v2 (id, name, active) SELECT id, name, active FROM lead_sources;
DROP TABLE lead_sources;
ALTER TABLE lead_sources_v2 RENAME TO lead_sources;
