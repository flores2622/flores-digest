-- Pantheon's own CRM (Frank, 2026-10-06: "i basically want to build my own,
-- built into Pantheon"). Cloudflare D1 (SQLite), binding CRM in wrangler.jsonc.
--
-- The shapes follow AgencyZoom's records on purpose: every id, status code and
-- field name the nightly and the Worker already read (az_client.py, site/live.js)
-- keeps its meaning, so the pipeline moves over by swapping the client, not by
-- rewriting the 45 modules that read lead / policy / task / SR records. An
-- imported row keeps AgencyZoom's id (crm_import.py); a row Pantheon creates
-- gets the next id above them. People are staff.json's az_id numbers
-- (assigned_to, agent_id, csr, created_by ...), so staff.json stays the one
-- staff list.
--
-- Status codes, as AgencyZoom's (CLAUDE.md; counted on the 2026-10-06 snapshot):
--   leads.status            0 open, 2 sold; 3 and 5 are AgencyZoom's closed
--                           states (deaded / cycled out), kept as they come
--   service_requests.status 0 deleted, 1 live, 2 completed
--   tasks.status            0 open, 1 completed, 2 closed without completion
--   policies.status         text: active (AZ 1), pending (AZ 3, the next term
--                           issued), expired (AZ 4, a past term), cancelled (AZ 0)
-- Dates are "YYYY-MM-DD HH:MM:SS" on the agency's clock (staff.json
-- agency.timezone), the way AgencyZoom's notes read; the API says which.

CREATE TABLE IF NOT EXISTS lead_sources (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  active INTEGER NOT NULL DEFAULT 1
);

-- Sales pipelines and service workflows are one table: kind says which.
CREATE TABLE IF NOT EXISTS workflows (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('sales', 'service')),
  active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS stages (
  id INTEGER PRIMARY KEY,
  workflow_id INTEGER NOT NULL REFERENCES workflows(id),
  name TEXT NOT NULL,
  ord INTEGER NOT NULL DEFAULT 0,
  active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS stages_workflow ON stages(workflow_id, ord);

CREATE TABLE IF NOT EXISTS service_categories (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS resolutions (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS carriers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  short TEXT,            -- the Sales sheet's name: Farmers / BW / Foremost
  active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS households (
  id INTEGER PRIMARY KEY,
  firstname TEXT NOT NULL DEFAULT '',
  lastname TEXT NOT NULL DEFAULT '',
  business_name TEXT,
  phone TEXT,
  phone_key TEXT,            -- last ten digits, az_corpus.e164's key
  secondary_phone TEXT,
  secondary_phone_key TEXT,
  email TEXT,
  address TEXT, city TEXT, state TEXT, zip TEXT,
  assigned_to INTEGER,       -- staff az_id
  customer_type TEXT NOT NULL DEFAULT 'customer',
  as_customer_date TEXT,
  create_date TEXT NOT NULL,
  modify_date TEXT,
  status INTEGER NOT NULL DEFAULT 1,   -- 1 active, 0 deleted
  notes_text TEXT,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS households_phone ON households(phone_key);
CREATE INDEX IF NOT EXISTS households_phone2 ON households(secondary_phone_key);
CREATE INDEX IF NOT EXISTS households_name ON households(lastname, firstname);

CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY,
  firstname TEXT NOT NULL DEFAULT '',
  lastname TEXT NOT NULL DEFAULT '',
  business_name TEXT,
  phone TEXT,
  phone_key TEXT,
  secondary_phone TEXT,
  secondary_phone_key TEXT,
  email TEXT,
  address TEXT, city TEXT, state TEXT, zip TEXT,
  language TEXT,
  assigned_to INTEGER,                 -- staff az_id
  lead_source_id INTEGER REFERENCES lead_sources(id),
  workflow_id INTEGER REFERENCES workflows(id),
  workflow_stage_id INTEGER REFERENCES stages(id),
  enter_stage_date TEXT,
  status INTEGER NOT NULL DEFAULT 0,   -- 0 open, 2 sold, 3 dead
  exit TEXT,                           -- Smart-Cycle / Dead / Sold (pipelines.EXITS)
  loss_reason TEXT,
  create_date TEXT NOT NULL,
  last_activity_date TEXT,
  quote_date TEXT,
  sold_date TEXT,
  converted_household_id INTEGER REFERENCES households(id),
  created_by INTEGER,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS leads_phone ON leads(phone_key);
CREATE INDEX IF NOT EXISTS leads_phone2 ON leads(secondary_phone_key);
CREATE INDEX IF NOT EXISTS leads_activity ON leads(last_activity_date);
CREATE INDEX IF NOT EXISTS leads_assigned ON leads(assigned_to, status);
CREATE INDEX IF NOT EXISTS leads_create ON leads(create_date);
CREATE INDEX IF NOT EXISTS leads_sold ON leads(sold_date);
CREATE INDEX IF NOT EXISTS leads_name ON leads(lastname, firstname);

CREATE TABLE IF NOT EXISTS policies (
  id INTEGER PRIMARY KEY,
  household_id INTEGER REFERENCES households(id),
  lead_id INTEGER REFERENCES leads(id),
  agent_id INTEGER,                    -- staff az_id: who sold it
  lead_source_id INTEGER REFERENCES lead_sources(id),
  carrier_id INTEGER REFERENCES carriers(id),
  carrier_name TEXT,
  policy_type_name TEXT,
  policy_number TEXT,
  premium REAL,
  term_months INTEGER,
  effective_date TEXT,
  expiry_date TEXT,
  sold_date TEXT,
  status TEXT NOT NULL DEFAULT 'active',   -- active / cancelled / expired / pending
  cancel_date TEXT,
  create_date TEXT NOT NULL,
  modify_date TEXT,
  created_by INTEGER,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS policies_agent_sold ON policies(agent_id, sold_date);
CREATE INDEX IF NOT EXISTS policies_household ON policies(household_id);
CREATE INDEX IF NOT EXISTS policies_lead ON policies(lead_id);
CREATE INDEX IF NOT EXISTS policies_expiry ON policies(expiry_date);

CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY,
  lead_id INTEGER NOT NULL REFERENCES leads(id),
  carrier_id INTEGER,
  carrier_name TEXT,
  policy_type_name TEXT,
  premium REAL,
  term_months INTEGER,
  quote_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'presented',   -- presented / sent / sold / lost
  created_by INTEGER,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS quotes_lead ON quotes(lead_id, quote_date);

-- Every note on a lead, household or SR: the stream the pipeline reads
-- (messages.py, lead_history.py, day_calls.py). `type` is AgencyZoom's --
-- CALL, TEXT, TEXT-FAILED, EMAIL, NOTE, TASK, MOVE_STAGE, QUOTE, SYSTEM.
-- `attr` is the JSON the type carries (outbound, triggerRuleId, emailSubject,
-- emailSnippet, lastOpenDate, bounced, bounceReason, contentType, direction).
-- `origin` says who typed it: person / automation / traq / ringcentral /
-- import.
CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY,
  lead_id INTEGER REFERENCES leads(id),
  household_id INTEGER REFERENCES households(id),
  sr_id INTEGER,
  type TEXT NOT NULL,
  body TEXT NOT NULL DEFAULT '',
  attr TEXT,                 -- JSON object
  attachments TEXT,          -- JSON list
  origin TEXT NOT NULL DEFAULT 'person',
  created_by INTEGER,
  create_date TEXT NOT NULL,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS notes_lead ON notes(lead_id, create_date);
CREATE INDEX IF NOT EXISTS notes_household ON notes(household_id, create_date);
CREATE INDEX IF NOT EXISTS notes_sr ON notes(sr_id, create_date);
CREATE INDEX IF NOT EXISTS notes_date ON notes(create_date);

-- A stage move kept structured (AgencyZoom only keeps the MOVE_STAGE note).
-- The API still hands lead_history a MOVE_STAGE note for each, so
-- pipelines.parse_move reads Pantheon's moves like AgencyZoom's.
CREATE TABLE IF NOT EXISTS stage_moves (
  id INTEGER PRIMARY KEY,
  lead_id INTEGER NOT NULL REFERENCES leads(id),
  from_where TEXT,           -- 'Pipeline | Stage', or an exit
  to_where TEXT NOT NULL,
  loss_reason TEXT,
  moved_by INTEGER,
  at TEXT NOT NULL,
  note_id INTEGER REFERENCES notes(id)
);
CREATE INDEX IF NOT EXISTS stage_moves_lead ON stage_moves(lead_id, at);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  comments TEXT,
  type TEXT NOT NULL DEFAULT 'call',   -- call / email / text / todo
  assignee_id INTEGER,                 -- staff az_id
  lead_id INTEGER REFERENCES leads(id),
  household_id INTEGER REFERENCES households(id),
  sr_id INTEGER,
  customer_type TEXT,                  -- lead / customer / serviceTicket (AgencyZoom's)
  due_date TEXT,
  status INTEGER NOT NULL DEFAULT 0,   -- 0 open, 1 completed
  complete_date TEXT,
  completed_by INTEGER,
  agency_todo INTEGER NOT NULL DEFAULT 0,
  created_by INTEGER,
  create_date TEXT NOT NULL,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS tasks_due ON tasks(due_date, assignee_id);
CREATE INDEX IF NOT EXISTS tasks_lead ON tasks(lead_id);
CREATE INDEX IF NOT EXISTS tasks_household ON tasks(household_id);
CREATE INDEX IF NOT EXISTS tasks_sr ON tasks(sr_id);

-- Service requests ("SR", never "ticket" on anything the agency reads).
CREATE TABLE IF NOT EXISTS service_requests (
  id INTEGER PRIMARY KEY,
  household_id INTEGER REFERENCES households(id),
  lead_id INTEGER REFERENCES leads(id),
  customer_type TEXT,
  workflow_id INTEGER REFERENCES workflows(id),
  workflow_stage_id INTEGER REFERENCES stages(id),
  enter_stage_date TEXT,
  category_id INTEGER REFERENCES service_categories(id),
  subject TEXT NOT NULL DEFAULT '',
  description TEXT,
  csr INTEGER,                          -- staff az_id: assigned to
  created_by INTEGER,
  create_date TEXT NOT NULL,
  due_date TEXT,
  expiry_date TEXT,
  effective_date TEXT,
  policy_id INTEGER REFERENCES policies(id),
  status INTEGER NOT NULL DEFAULT 1,    -- 0 deleted, 1 live, 2 completed
  complete_date TEXT,
  completed_by INTEGER,
  resolution_id INTEGER REFERENCES resolutions(id),
  resolution_desc TEXT,
  modify_date TEXT,
  modified_by INTEGER,
  az_id INTEGER
);
CREATE INDEX IF NOT EXISTS srs_status ON service_requests(status, workflow_id);
CREATE INDEX IF NOT EXISTS srs_household ON service_requests(household_id);
CREATE INDEX IF NOT EXISTS srs_complete ON service_requests(complete_date);
CREATE INDEX IF NOT EXISTS srs_create ON service_requests(create_date);
CREATE INDEX IF NOT EXISTS srs_csr ON service_requests(csr, status);

-- Every write, who made it and what changed: the audit trail AgencyZoom
-- never gave us. `before` / `after` are the changed fields only.
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  who TEXT NOT NULL,            -- the Access email
  object TEXT NOT NULL,         -- lead / household / policy / quote / note / task / sr / move
  object_id INTEGER NOT NULL,
  action TEXT NOT NULL,         -- create / update / complete / move / import
  before TEXT,                  -- JSON
  after TEXT                    -- JSON
);
CREATE INDEX IF NOT EXISTS events_object ON events(object, object_id, at);
CREATE INDEX IF NOT EXISTS events_at ON events(at);
