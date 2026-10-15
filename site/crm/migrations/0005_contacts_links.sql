-- Contacts and linked accounts (Frank, 2026-10-14: "i want to make sure that
-- feature is available on my system as well"; CRM.md phase 3).
--
-- AgencyZoom's customer page has three sections its public API never returns:
--   Contacts   the people on an account, one of them PRIMARY (the account
--              holder; Claudia A Gallardo's account lists Claudia, primary,
--              and Celerino; Norma De Leon's lists four);
--   Customers  other ACCOUNTS linked to it (Claudia <-> Celerino A. Gallardo,
--              L.L.C.; Norma <-> Nordell Inc, Delato Corp, Los Choches LLC,
--              Meli's Inc) -- the link shows on both sides;
--   Leads      the leads that became it (leads.converted_household_id).
-- A contact is its own record and can sit on several accounts (Claudia and
-- Celerino are contacts on the LLC as well as on Claudia's own account), each
-- account with its own primary. These are Pantheon's own rows (az_id stays
-- NULL): nothing mirrors them from AgencyZoom, so the nightly never touches
-- them. A household with no household_contacts rows is shown with its own
-- name, phone and email as its one primary contact until the first write
-- (site/crm.js ensureContacts makes it real).
CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL DEFAULT '',
  middlename TEXT,
  lastname TEXT NOT NULL DEFAULT '',
  email TEXT,
  phone TEXT,
  phone_key TEXT,
  birthday TEXT,
  create_date TEXT NOT NULL,
  created_by INTEGER,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS contacts_name ON contacts(lastname, firstname);
CREATE INDEX IF NOT EXISTS contacts_phone ON contacts(phone_key);

CREATE TABLE IF NOT EXISTS household_contacts (
  household_id INTEGER NOT NULL REFERENCES households(id),
  contact_id INTEGER NOT NULL REFERENCES contacts(id),
  is_primary INTEGER NOT NULL DEFAULT 0,   -- the account holder; at most one per household
  relationship TEXT,
  added_at TEXT NOT NULL,
  added_by INTEGER,
  PRIMARY KEY (household_id, contact_id)
);
CREATE INDEX IF NOT EXISTS household_contacts_contact ON household_contacts(contact_id);

-- One row per linked pair, the lower id first, read from either side.
CREATE TABLE IF NOT EXISTS household_links (
  household_a INTEGER NOT NULL REFERENCES households(id),
  household_b INTEGER NOT NULL REFERENCES households(id),
  added_at TEXT NOT NULL,
  added_by INTEGER,
  PRIMARY KEY (household_a, household_b),
  CHECK (household_a < household_b)
);
CREATE INDEX IF NOT EXISTS household_links_b ON household_links(household_b);
