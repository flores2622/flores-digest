-- Frank's own lists, and the map from AgencyZoom's ids onto them (CRM.md,
-- "Consolidating the lists"; Frank, 2026-10-06: "i want to consolidate lead
-- sources, pipelines, service request categories. I want to customize and
-- rebuild"). AgencyZoom's lookups (lead_sources, workflows, stages,
-- service_categories) stay as they are and every record keeps AgencyZoom's
-- ids; the pages read THROUGH list_map to show Frank's names. An AgencyZoom
-- entry with no map row is Unsorted on the Lists page until Frank places it.
--
-- lists.kind    source   a lead source (Winback, Internet lead, Call-in / Walk-in ...)
--               pipeline a sales pipeline (New Business, Quotes Not Closed ...)
--               stage    a stage; parent_id is its pipeline's or service pipeline's id
--               service  a service pipeline, which IS the SR category (Frank,
--                        2026-10-06: "the category is really the service
--                        pipeline it goes into"): Billing, Contingencies,
--                        Personal Renewals, Personal Endorsements, Commercial
--                        Renewals, Commercial Endorsements, Claims
-- detail_label  the one field kept beside the entry instead of a list of its
--               own: "How they found us" on Call-in / Walk-in, "Vendor" on
--               Internet lead, "Partner" on Lender referral, "Staff member" on
--               Personal network, "Claim type" on Claims, "Payment" on Billing
-- list_map.kind source | workflow | stage | category -- which AgencyZoom table
--               az_id is from; list_id is the lists row it is placed under
--               (kind source -> source, workflow -> pipeline or service, stage
--               -> stage, category -> service). A category with list_id NULL
--               follows its SR's workflow (General, UNASSIGNED).
-- detail        this AgencyZoom entry's value of the field: "Google" for the
--               Google source under Call-in / Walk-in, "Guild Mortgage (Nellie
--               Robertson)" under Lender referral.
-- placed_by     'rule' when crm_lists.py placed it by name, else the Access
--               email of whoever placed it on the Lists page. The nightly
--               writes INSERT OR IGNORE, so a placement made by hand stays.
CREATE TABLE IF NOT EXISTS lists (
  kind TEXT NOT NULL CHECK (kind IN ('source', 'pipeline', 'stage', 'service')),
  id INTEGER NOT NULL,
  name TEXT NOT NULL,
  parent_id INTEGER,
  detail_label TEXT,
  meaning TEXT,
  ord INTEGER NOT NULL DEFAULT 0,
  active INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (kind, id)
);
CREATE TABLE IF NOT EXISTS list_map (
  kind TEXT NOT NULL CHECK (kind IN ('source', 'workflow', 'stage', 'category')),
  az_id INTEGER NOT NULL,
  list_id INTEGER,
  detail TEXT,
  placed_by TEXT NOT NULL DEFAULT 'rule',
  PRIMARY KEY (kind, az_id)
);
