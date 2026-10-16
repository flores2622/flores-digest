-- Who the account holder IS (Frank, 2026-10-16: "if we never speak with
-- Claudia and always with Celerino, we should be able to make him the
-- account holder"). Making a contact the holder (site/crm.js, op "primary")
-- makes the account carry THEIR name, phone and email. The nightly mirror
-- copies AgencyZoom's name / phone / email onto an imported household
-- whenever AgencyZoom's copy changes, which would put the old holder back --
-- so a household with a row here keeps its name, phone and email whatever
-- AgencyZoom says (crm_import.statement), and `original` keeps what
-- AgencyZoom had when the holder was first changed (shown on the account's
-- page). Contact and phone fields only ever follow the holder from here.
CREATE TABLE IF NOT EXISTS household_holder (
  household_id INTEGER PRIMARY KEY REFERENCES households(id),
  set_at TEXT NOT NULL,
  set_by INTEGER,
  original TEXT           -- JSON: firstname, lastname, phone, email as AgencyZoom had them
);
