/* Pantheon's own CRM (Frank, 2026-10-06: "i basically want to build my own,
   built into Pantheon"). The data layer: Cloudflare D1 (binding CRM, schema
   in site/crm/migrations/) behind /api/crm/..., the same Access gate as the
   rest of the Worker.

   Who may call it: staff.json's `crm` board key -- Frank alone until further
   notice (2026-10-06). Everyone else gets 403 and the Tasks page never
   enters their menu (site/public/tasks.js probes /api/crm/lookups).

   THE API IS AGENCYZOOM-SHAPED ON PURPOSE. Each record comes back with the
   field names the nightly and the live refresh already read (id, firstname,
   lastname, phone, assignedTo, leadSourceId, leadSourceName, status,
   createDate, lastActivityDate, soldDate, convertedHouseholdId,
   workflowStageId ...; a policy's agentId, soldDate, premium, policyTypeName,
   carrierId, leadSourceId; a task's assigneeId, dueDate, status, customerId,
   customerType; an SR's workflowName, workflowStageName, csr, createDate,
   completeDate, resolutionId, status 0/1/2), lists page from page=0 like
   /v1/api/leads/list, and a lead's notes come newest first with a MOVE_STAGE
   note for every stage move -- so az_client.py / live.js move to Pantheon by
   swapping the client, and every rule in CLAUDE.md keeps meaning the same
   thing. People are staff.json's az_id numbers. Dates are "YYYY-MM-DD
   HH:MM:SS" on the agency's clock (staff.js localStr), never UTC.

     GET  /api/crm/lookups                 lead sources, workflows + stages,
                                           categories, resolutions, carriers,
                                           employees (staff.json)
     GET  /api/crm/search?phone=|q=        leads, households and SRs on a number
                                           (az_corpus.e164's key) or a name
     GET  /api/crm/<obj>?...               list (filters below), page=, limit=
     POST /api/crm/<obj>                   create
     GET  /api/crm/<obj>/<id>              one record
     POST /api/crm/<obj>/<id>              update (editable fields only)
     GET|POST /api/crm/<leads|households|srs>/<id>/notes
     GET|POST /api/crm/leads/<id>/quotes
     POST /api/crm/leads/<id>/move         {to: "1 Pipeline | Quoted" | "Dead" |
                                           "Smart-Cycle", why}
     POST /api/crm/leads/<id>/sold         {householdId?}: status 2, soldDate,
                                           converts to a household if none
     POST /api/crm/tasks/<id>/complete
     POST /api/crm/srs/<id>/complete       {resolutionId, note?}
     GET  /api/crm/events?object=&id=      the audit trail of one record
     GET  /api/crm/lists                   Frank's lists (lead sources, sales
                                           pipelines with stages, service
                                           pipelines) and every AgencyZoom
                                           entry's place under them, with counts
     POST /api/crm/lists                   {op: add|edit|order, kind, ...}
     POST /api/crm/lists/place             {kind, azId, listId, detail}
   <obj> is leads, households, policies, quotes, tasks or srs. Every write
   lands in `events` with the Access email, before and after.

   FRANK'S LISTS (CRM.md, "Consolidating the lists"; crm_lists.py): AgencyZoom's
   lookups and ids stay on every record, and each record ALSO carries Frank's
   name for it, read through list_map -- a lead's sourceName / sourceDetail /
   pipelineName / stageName, a policy's sourceName, an SR's pipelineName /
   pipelineDetail (its category's place, else its workflow's). The
   AgencyZoom-shaped fields (leadSourceName, workflowName ...) are untouched.

   Nothing here reads AgencyZoom, RingCentral or Insightful. Without the CRM
   binding every call answers 503 "CRM is not configured", like Coeus with no
   key, so a deploy before the database exists breaks nothing else. */

import { hasBoard, personByEmail, personById, PEOPLE, localStr } from "./staff.js";

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

/* ---- the objects ----------------------------------------------------------
   api name -> column, with a type for validation:
     text | int | num | bool | date (YYYY-MM-DD) | datetime (YYYY-MM-DD HH:MM:SS,
     a bare date is accepted and read as midnight) | json | enum:a|b|c
   `create` lists what a POST may set, `edit` what an update may change,
   `required` what a create must carry. Server-kept columns (phone keys,
   create_date, status changes through actions) are never writable directly. */
const PHONE = { phone: ["phone", "text"], secondaryPhone: ["secondary_phone", "text"] };
const PERSON = ["firstname", "lastname", "businessName", "email", "address", "city", "state", "zip"];
const COMMON = {
  firstname: ["firstname", "text"], lastname: ["lastname", "text"], businessName: ["business_name", "text"],
  email: ["email", "text"], address: ["address", "text"], city: ["city", "text"], state: ["state", "text"], zip: ["zip", "text"],
};

// The name and phone of whoever a task or SR hangs off: its lead, else its
// household. `t` is the main table in every list / getOne query.
const CUSTOMER_JOIN = {
  select: "coalesce(nullif(trim(l.firstname || ' ' || l.lastname), ''), l.business_name, nullif(trim(h.firstname || ' ' || h.lastname), ''), h.business_name) AS customer_name, coalesce(l.phone, h.phone) AS customer_phone",
  sql: "LEFT JOIN leads l ON l.id = t.lead_id LEFT JOIN households h ON h.id = t.household_id",
};

export const OBJECTS = {
  leads: {
    table: "leads", key: "leads", label: "lead",
    fields: {
      id: ["id", "int"], ...COMMON, ...PHONE, language: ["language", "text"],
      assignedTo: ["assigned_to", "int"], leadSourceId: ["lead_source_id", "int"],
      workflowId: ["workflow_id", "int"], workflowStageId: ["workflow_stage_id", "int"],
      enterStageDate: ["enter_stage_date", "datetime"], status: ["status", "int"], exit: ["exit", "text"],
      lossReason: ["loss_reason", "text"], createDate: ["create_date", "datetime"],
      lastActivityDate: ["last_activity_date", "datetime"], quoteDate: ["quote_date", "datetime"],
      soldDate: ["sold_date", "datetime"], convertedHouseholdId: ["converted_household_id", "int"],
      createdBy: ["created_by", "int"], azId: ["az_id", "int"],
    },
    create: [...PERSON, "phone", "secondaryPhone", "language", "assignedTo", "leadSourceId", "workflowId", "workflowStageId"],
    edit: [...PERSON, "phone", "secondaryPhone", "language", "assignedTo", "leadSourceId"],
    required: ["lastname"],
    filters: {
      status: "status = ?", assignedTo: "assigned_to = ?", leadSourceId: "lead_source_id = ?",
      workflowId: "workflow_id = ?", workflowStageId: "workflow_stage_id = ?",
      since: "last_activity_date >= ?", createdFrom: "create_date >= ?", createdTo: "create_date < ?",
      soldFrom: "sold_date >= ?", soldTo: "sold_date < ?", householdId: "converted_household_id = ?",
    },
    order: "last_activity_date DESC, id DESC",
  },
  households: {
    table: "households", key: "customers", label: "household",
    fields: {
      id: ["id", "int"], ...COMMON, ...PHONE, assignedTo: ["assigned_to", "int"],
      customerType: ["customer_type", "text"], asCustomerDate: ["as_customer_date", "datetime"],
      createDate: ["create_date", "datetime"], modifyDate: ["modify_date", "datetime"], status: ["status", "int"],
      notes: ["notes_text", "text"], azId: ["az_id", "int"],
    },
    create: [...PERSON, "phone", "secondaryPhone", "assignedTo", "customerType", "asCustomerDate", "notes"],
    edit: [...PERSON, "phone", "secondaryPhone", "assignedTo", "customerType", "notes"],
    required: ["lastname"],
    filters: { assignedTo: "assigned_to = ?", status: "status = ?", createdFrom: "create_date >= ?", createdTo: "create_date < ?",
      customerFrom: "as_customer_date >= ?", customerTo: "as_customer_date < ?" },
    order: "modify_date DESC, id DESC",
  },
  policies: {
    table: "policies", key: "policies", label: "policy",
    fields: {
      id: ["id", "int"], householdId: ["household_id", "int"], leadId: ["lead_id", "int"], agentId: ["agent_id", "int"],
      leadSourceId: ["lead_source_id", "int"], carrierId: ["carrier_id", "int"], carrierName: ["carrier_name", "text"],
      policyTypeName: ["policy_type_name", "text"], policyNumber: ["policy_number", "text"], premium: ["premium", "num"],
      term: ["term_months", "int"], effectiveDate: ["effective_date", "date"], expiryDate: ["expiry_date", "date"],
      soldDate: ["sold_date", "date"], status: ["status", "enum:active|cancelled|expired|pending"],
      cancelDate: ["cancel_date", "date"], createDate: ["create_date", "datetime"], modifyDate: ["modify_date", "datetime"],
      createdBy: ["created_by", "int"], azId: ["az_id", "int"],
    },
    create: ["householdId", "leadId", "agentId", "leadSourceId", "carrierId", "carrierName", "policyTypeName", "policyNumber",
      "premium", "term", "effectiveDate", "expiryDate", "soldDate", "status"],
    edit: ["householdId", "leadId", "agentId", "leadSourceId", "carrierId", "carrierName", "policyTypeName", "policyNumber",
      "premium", "term", "effectiveDate", "expiryDate", "soldDate", "status", "cancelDate"],
    required: ["agentId", "policyTypeName", "soldDate"],
    filters: { agentId: "agent_id = ?", householdId: "household_id = ?", leadId: "lead_id = ?", status: "status = ?",
      soldFrom: "sold_date >= ?", soldTo: "sold_date <= ?", expiryFrom: "expiry_date >= ?", expiryTo: "expiry_date <= ?",
      carrierId: "carrier_id = ?" },
    order: "sold_date DESC, id DESC",
  },
  quotes: {
    table: "quotes", key: "quotes", label: "quote",
    fields: {
      id: ["id", "int"], leadId: ["lead_id", "int"], carrierId: ["carrier_id", "int"], carrierName: ["carrier_name", "text"],
      policyTypeName: ["policy_type_name", "text"], premium: ["premium", "num"], term: ["term_months", "int"],
      quoteDate: ["quote_date", "datetime"], status: ["status", "enum:presented|sent|sold|lost"],
      createdBy: ["created_by", "int"], azId: ["az_id", "int"],
    },
    create: ["leadId", "carrierId", "carrierName", "policyTypeName", "premium", "term", "quoteDate", "status"],
    edit: ["carrierId", "carrierName", "policyTypeName", "premium", "term", "status"],
    required: ["leadId", "policyTypeName"],
    filters: { leadId: "lead_id = ?", status: "status = ?", quotedFrom: "quote_date >= ?", quotedTo: "quote_date < ?" },
    order: "quote_date DESC, id DESC",
  },
  tasks: {
    table: "tasks", key: "tasks", label: "task",
    fields: {
      id: ["id", "int"], title: ["title", "text"], comments: ["comments", "text"], type: ["type", "enum:call|email|text|todo"],
      assigneeId: ["assignee_id", "int"], leadId: ["lead_id", "int"], householdId: ["household_id", "int"], srId: ["sr_id", "int"],
      customerType: ["customer_type", "text"], dueDate: ["due_date", "datetime"], status: ["status", "int"],
      completeDate: ["complete_date", "datetime"], completedBy: ["completed_by", "int"], agencyTodo: ["agency_todo", "bool"],
      createdBy: ["created_by", "int"], createDate: ["create_date", "datetime"], azId: ["az_id", "int"],
    },
    create: ["title", "comments", "type", "assigneeId", "leadId", "householdId", "srId", "dueDate", "agencyTodo"],
    edit: ["title", "comments", "type", "assigneeId", "dueDate", "agencyTodo"],
    required: ["title", "assigneeId"],
    filters: { assigneeId: "assignee_id = ?", status: "status = ?", leadId: "lead_id = ?", householdId: "household_id = ?",
      srId: "sr_id = ?", dueFrom: "due_date >= ?", dueTo: "due_date < ?", completedFrom: "complete_date >= ?",
      completedTo: "complete_date < ?" },
    order: "due_date ASC, id ASC",
    joins: CUSTOMER_JOIN,
  },
  srs: {
    table: "service_requests", key: "serviceTickets", label: "SR",
    fields: {
      id: ["id", "int"], householdId: ["household_id", "int"], leadId: ["lead_id", "int"], customerType: ["customer_type", "text"],
      workflowId: ["workflow_id", "int"], workflowStageId: ["workflow_stage_id", "int"], enterStageDate: ["enter_stage_date", "datetime"],
      categoryId: ["category_id", "int"], subject: ["subject", "text"], description: ["description", "text"], csr: ["csr", "int"],
      createdBy: ["created_by", "int"], createDate: ["create_date", "datetime"], dueDate: ["due_date", "datetime"],
      expiryDate: ["expiry_date", "date"], effectiveDate: ["effective_date", "date"], policyId: ["policy_id", "int"],
      status: ["status", "int"], completeDate: ["complete_date", "datetime"], completedBy: ["completed_by", "int"],
      resolutionId: ["resolution_id", "int"], resolutionDesc: ["resolution_desc", "text"], modifyDate: ["modify_date", "datetime"],
      modifiedBy: ["modified_by", "int"], azId: ["az_id", "int"],
    },
    create: ["householdId", "leadId", "workflowId", "workflowStageId", "categoryId", "subject", "description", "csr", "dueDate",
      "expiryDate", "effectiveDate", "policyId"],
    edit: ["householdId", "leadId", "workflowStageId", "categoryId", "subject", "description", "csr", "dueDate", "expiryDate",
      "effectiveDate", "policyId"],
    required: ["workflowId", "subject"],
    filters: { status: "status = ?", workflowId: "workflow_id = ?", workflowStageId: "workflow_stage_id = ?", csr: "csr = ?",
      householdId: "household_id = ?", leadId: "lead_id = ?", categoryId: "category_id = ?", policyId: "policy_id = ?",
      createdFrom: "create_date >= ?", createdTo: "create_date < ?", completedFrom: "complete_date >= ?",
      completedTo: "complete_date < ?" },
    order: "create_date DESC, id DESC",
    joins: CUSTOMER_JOIN,
  },
};
const NOTE_PARENT = { leads: "lead_id", households: "household_id", srs: "sr_id" };
const NOTE_TYPES = new Set(["CALL", "TEXT", "TEXT-FAILED", "EMAIL", "NOTE", "TASK", "MOVE_STAGE", "QUOTE", "SYSTEM"]);
const EXITS = new Set(["Smart-Cycle", "Dead", "Sold"]);   // pipelines.EXITS
const MAX_LIMIT = 500;

/* ---- values ---------------------------------------------------------------- */
/** az_corpus.e164's key: "+1" + the last ten digits, or null. */
export function phoneKey(raw) {
  const d = String(raw || "").replace(/\D/g, "");
  if (d.length < 10 || d.length > 15) return null;
  return "+1" + d.slice(-10);
}
const DATE = /^\d{4}-\d{2}-\d{2}$/;
/** "2026-10-06" -> "2026-10-07" (calendar arithmetic, no zone). */
export function nextDay(day) {
  const [y, m, d] = day.split("-").map(Number);
  const t = new Date(Date.UTC(y, m - 1, d + 1));
  return `${t.getUTCFullYear()}-${String(t.getUTCMonth() + 1).padStart(2, "0")}-${String(t.getUTCDate()).padStart(2, "0")}`;
}
const DATETIME = /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$/;
/** Check one value against a field type; returns [ok, value] with the value normalised. */
export function checkValue(type, v) {
  if (v === null || v === undefined || v === "") return [true, null];
  if (type === "text") return [typeof v === "string" && v.length <= 4000, typeof v === "string" ? v.trim() : v];
  if (type === "int") return [Number.isInteger(Number(v)) && String(v).trim() !== "", Number(v)];
  if (type === "num") return [Number.isFinite(Number(v)), Number(v)];
  if (type === "bool") return [typeof v === "boolean" || v === 0 || v === 1, v ? 1 : 0];
  if (type === "date") return [typeof v === "string" && DATE.test(v.trim()), typeof v === "string" ? v.trim() : v];
  if (type === "datetime") {
    if (typeof v !== "string") return [false, v];
    const s = v.trim();
    if (DATE.test(s)) return [true, s + " 00:00:00"];
    if (!DATETIME.test(s)) return [false, s];
    const t = s.replace("T", " ");
    return [true, t.length === 16 ? t + ":00" : t];
  }
  if (type === "json") return [typeof v === "object", JSON.stringify(v)];
  if (type.startsWith("enum:")) return [type.slice(5).split("|").includes(v), v];
  return [false, v];
}
/** The writable part of a request body for `spec`, or {error}. `allowed` is spec.create or spec.edit. */
function pick(spec, body, allowed, needRequired) {
  if (!body || typeof body !== "object" || Array.isArray(body)) return { error: "a JSON object is expected" };
  const cols = {}, api = {};
  for (const [k, v] of Object.entries(body)) {
    if (!allowed.includes(k)) return { error: `${k} cannot be set on a ${spec.label}` };
    const [col, type] = spec.fields[k];
    const [ok, val] = checkValue(type, v);
    if (!ok) return { error: `${k}: not a ${type}` };
    cols[col] = val; api[k] = val;
  }
  if (needRequired) for (const k of spec.required) if (api[k] === undefined || api[k] === null) return { error: `${k} is required` };
  return { cols, api };
}
/** Phone key columns kept beside every phone. */
function withPhoneKeys(cols) {
  if ("phone" in cols) cols.phone_key = phoneKey(cols.phone);
  if ("secondary_phone" in cols) cols.secondary_phone_key = phoneKey(cols.secondary_phone);
  return cols;
}

/* ---- rows -> API records ----------------------------------------------------- */
function personName(id) { const p = personById(id); return p ? p.name : null; }
function rowToApi(spec, row, lk) {
  if (!row) return null;
  const out = {};
  for (const [k, [col, type]] of Object.entries(spec.fields)) {
    let v = row[col];
    if (v === undefined) continue;
    if (type === "bool") v = !!v;
    out[k] = v;
  }
  if (spec.table === "leads") {
    out.leadSourceName = lk.sources.get(out.leadSourceId) || null;
    out.workflowName = lk.workflows.get(out.workflowId) || null;
    out.workflowStageName = lk.stages.get(out.workflowStageId) || null;
    out.assignedToName = personName(out.assignedTo);
    out.name = `${out.firstname || ""} ${out.lastname || ""}`.trim();
    const pl = lk.placed, src = pl && pl.source.get(out.leadSourceId), wf = pl && pl.workflow.get(out.workflowId), st = pl && pl.stage.get(out.workflowStageId);
    out.sourceName = src ? src.name : null; out.sourceDetail = src ? src.detail : null;
    out.pipelineName = wf && wf.kind === "pipeline" ? wf.name : null;
    out.stageName = st ? st.name : null;
  } else if (spec.table === "households") {
    out.name = out.businessName || `${out.firstname || ""} ${out.lastname || ""}`.trim();
    out.assignedToName = personName(out.assignedTo);
  } else if (spec.table === "policies") {
    out.agentName = personName(out.agentId);
    out.leadSourceName = lk.sources.get(out.leadSourceId) || null;
    const src = lk.placed && lk.placed.source.get(out.leadSourceId);
    out.sourceName = src ? src.name : null; out.sourceDetail = src ? src.detail : null;
    if (!out.carrierName && out.carrierId) out.carrierName = lk.carriers.get(out.carrierId) || null;
  } else if (spec.table === "tasks") {
    out.assignees = out.assigneeId ? [{ id: out.assigneeId, name: personName(out.assigneeId) }] : [];
    // AgencyZoom's own shape for what a task hangs off.
    out.customerId = out.leadId || out.householdId || out.srId || null;
    out.customerType = out.customerType || (out.leadId ? "lead" : out.householdId ? "customer" : out.srId ? "serviceTicket" : null);
    out.customerName = row.customer_name || null;
    out.customerPhone = row.customer_phone || null;
  } else if (spec.table === "service_requests") {
    out.workflowName = lk.workflows.get(out.workflowId) || null;
    out.workflowStageName = lk.stages.get(out.workflowStageId) || null;
    const p = personById(out.csr);
    out.csrFirstname = p ? p.name.split(" ")[0] : null;
    out.categoryName = lk.categories.get(out.categoryId) || null;
    const sp = lk.placed ? srPipeline(lk.placed, out.categoryId, out.workflowId) : null;
    out.pipelineName = sp ? sp.name : null; out.pipelineDetail = sp ? sp.detail : null;
    if (!out.resolutionDesc && out.resolutionId) out.resolutionDesc = lk.resolutions.get(out.resolutionId) || null;
    out.customerId = out.householdId || out.leadId || null;
    out.customerName = row.customer_name || null;
    out.customerPhone = row.customer_phone || null;
  }
  return out;
}
function noteToApi(r) {
  return { id: r.id, type: r.type, body: r.body, createDate: r.create_date, createdBy: r.created_by,
    createdByName: personName(r.created_by), origin: r.origin,
    attr: r.attr ? JSON.parse(r.attr) : {}, attachments: r.attachments ? JSON.parse(r.attachments) : [],
    leadId: r.lead_id, householdId: r.household_id, srId: r.sr_id };
}

/* ---- Frank's lists and the map ------------------------------------------------- */
const LIST_KINDS = new Set(["source", "pipeline", "stage", "service"]);
const MAP_KINDS = new Set(["source", "workflow", "stage", "category"]);
function listToApi(x) {
  return { id: x.id, name: x.name, parentId: x.parent_id, detailLabel: x.detail_label, meaning: x.meaning, ord: x.ord, active: !!x.active };
}
/** The lists and list_map rows; empty before migration 0004 (the tables are made
    by the first sync after a deploy, or `wrangler d1 migrations apply`). */
async function listTables(db) {
  try {
    const [l, m] = await db.batch([
      db.prepare("SELECT kind, id, name, parent_id, detail_label, meaning, ord, active FROM lists ORDER BY kind, ord, id"),
      db.prepare("SELECT kind, az_id, list_id, detail, placed_by FROM list_map"),
    ]);
    return { lists: (l.results || []).map(listToApi).map((x, i) => ({ ...x, kind: (l.results || [])[i].kind })), map: m.results || [], ready: true };
  } catch (_) {
    return { lists: [], map: [], ready: false };
  }
}
/** lists grouped by kind, stages under their pipeline. */
function listsByKind(lists) {
  const out = { source: [], pipeline: [], stage: [], service: [] };
  for (const x of lists) if (out[x.kind]) out[x.kind].push(x);
  for (const p of [...out.pipeline, ...out.service]) p.stages = out.stage.filter((s) => s.parentId === p.id);
  return out;
}
/** az id -> Frank's entry, per map kind, for rowToApi. `wfKinds` is az workflow
    id -> "sales" | "service": a sales workflow is placed under a pipeline, a
    service one under a service pipeline (their ids overlap). */
function placedMaps(t, wfKinds = new Map()) {
  const by = {};
  for (const x of t.lists) by[`${x.kind}:${x.id}`] = x;
  const stageParent = new Map(t.lists.filter((x) => x.kind === "stage").map((x) => [x.id, x.parentId]));
  const wfKind = new Map();   // az workflow id -> "pipeline" | "service" (which list kind it is placed in)
  const out = { source: new Map(), workflow: new Map(), stage: new Map(), category: new Map(), ready: t.ready, wfKind };
  for (const m of t.map) {
    if (m.kind === "source") { const e = by[`source:${m.list_id}`]; if (e) out.source.set(m.az_id, { id: e.id, name: e.name, detail: m.detail, label: e.detailLabel }); }
    else if (m.kind === "workflow") {
      const k = wfKinds.get(m.az_id);
      const e = k === "service" ? by[`service:${m.list_id}`] : k === "sales" ? by[`pipeline:${m.list_id}`] : (by[`pipeline:${m.list_id}`] || by[`service:${m.list_id}`]);
      if (e) { out.workflow.set(m.az_id, { id: e.id, name: e.name, kind: e.kind, detail: m.detail }); wfKind.set(m.az_id, e.kind); }
    } else if (m.kind === "stage") { const e = by[`stage:${m.list_id}`]; if (e) out.stage.set(m.az_id, { id: e.id, name: e.name, pipelineId: stageParent.get(e.id) }); }
    else if (m.kind === "category") {
      const e = m.list_id == null ? null : by[`service:${m.list_id}`];
      out.category.set(m.az_id, e ? { id: e.id, name: e.name, detail: m.detail, label: e.detailLabel } : { id: null, name: null, detail: m.detail, follows: true });
    }
  }
  return out;
}
/** An SR's service pipeline: its category's place, else its workflow's. */
function srPipeline(pl, categoryId, workflowId) {
  const c = categoryId != null ? pl.category.get(categoryId) : null;
  if (c && c.id != null) return { name: c.name, detail: c.detail };
  const w = workflowId != null ? pl.workflow.get(workflowId) : null;
  if (w && w.kind === "service") return { name: w.name, detail: (c && c.detail) || w.detail || null };
  return null;
}

/* ---- lookups --------------------------------------------------------------- */
async function lookups(db) {
  const [s, w, st, c, r, ca] = await db.batch([
    db.prepare("SELECT id, name, active FROM lead_sources ORDER BY name"),
    db.prepare("SELECT id, name, kind, active FROM workflows ORDER BY kind, name"),
    db.prepare("SELECT id, workflow_id, name, ord, active FROM stages ORDER BY workflow_id, ord, id"),
    db.prepare("SELECT id, name, active FROM service_categories ORDER BY name"),
    db.prepare("SELECT id, name, active FROM resolutions ORDER BY name"),
    db.prepare("SELECT id, name, short, active FROM carriers ORDER BY name"),
  ]);
  const rows = (x) => (x && x.results) || [];
  const stagesByWf = {};
  for (const x of rows(st)) (stagesByWf[x.workflow_id] = stagesByWf[x.workflow_id] || []).push({ id: x.id, name: x.name, ord: x.ord, active: !!x.active });
  const t = await listTables(db);
  const byKind = listsByKind(t.lists);
  return {
    lists: { ready: t.ready, sources: byKind.source, pipelines: byKind.pipeline, service: byKind.service },
    leadSources: rows(s).map((x) => ({ id: x.id, name: x.name, active: !!x.active })),
    workflows: rows(w).map((x) => ({ id: x.id, name: x.name, kind: x.kind, active: !!x.active, stages: stagesByWf[x.id] || [] })),
    serviceCategories: rows(c).map((x) => ({ id: x.id, name: x.name, active: !!x.active })),
    resolutions: rows(r).map((x) => ({ id: x.id, name: x.name, active: !!x.active })),
    carriers: rows(ca).map((x) => ({ id: x.id, name: x.name, short: x.short, active: !!x.active })),
    employees: PEOPLE.filter((p) => p.az_id).map((p) => ({ id: p.az_id, name: p.name, firstname: p.name.split(" ")[0],
      lastname: p.name.split(" ").slice(1).join(" "), producer: !!p.producer, service: !!p.service })),
  };
}
/** The name maps rowToApi joins with. */
async function nameMaps(db) {
  const lk = await lookups(db);
  const m = (list) => new Map(list.map((x) => [x.id, x.name]));
  const stages = new Map();
  for (const w of lk.workflows) for (const s of w.stages) stages.set(s.id, s.name);
  return { sources: m(lk.leadSources), workflows: m(lk.workflows), stages, categories: m(lk.serviceCategories),
    resolutions: m(lk.resolutions), carriers: m(lk.carriers), placed: placedMaps(await listTables(db), new Map(lk.workflows.map((w) => [w.id, w.kind]))),
    stageWorkflow: new Map(lk.workflows.flatMap((w) => w.stages.map((s) => [s.id, w.id]))),
    whereOf: new Map(lk.workflows.flatMap((w) => w.stages.map((s) => [`${w.name} | ${s.name}`, { workflowId: w.id, stageId: s.id }]))) };
}

/* ---- events ---------------------------------------------------------------- */
function eventStmt(db, who, object, id, action, before, after) {
  return db.prepare("INSERT INTO events (at, who, object, object_id, action, before, after) VALUES (?, ?, ?, ?, ?, ?, ?)")
    .bind(localStr(), who, object, id, action, before ? JSON.stringify(before) : null, after ? JSON.stringify(after) : null);
}
/** The columns of `after` that differ from `row`, as API names, for the event. */
function changed(spec, row, cols) {
  const before = {}, after = {};
  const byCol = Object.fromEntries(Object.entries(spec.fields).map(([k, [c]]) => [c, k]));
  for (const [c, v] of Object.entries(cols)) {
    if (!byCol[c]) continue;
    if ((row[c] ?? null) === (v ?? null)) continue;
    before[byCol[c]] = row[c] ?? null; after[byCol[c]] = v ?? null;
  }
  return { before, after };
}

/* ---- the generic reads and writes ----------------------------------------------- */
async function list(db, spec, url, lk) {
  const where = [], args = [];
  const typeOfCol = (col) => (Object.values(spec.fields).find(([c]) => c === col) || [null, "int"])[1];
  for (const [k, sql] of Object.entries(spec.filters)) {
    const v = url.searchParams.get(k);
    if (v === null || v === "") continue;
    const col = sql.split(" ")[0];
    const type = typeOfCol(col);
    let [ok, val] = checkValue(type === "enum" || type.startsWith("enum:") ? "text" : type, v);
    if (!ok) return json({ error: `${k}: bad value` }, 400);
    // A bare day on a datetime column: "from" is that midnight, "to" runs
    // through the end of that day (the next midnight, exclusive). A full
    // datetime is used as given. A date column compares days as typed.
    if (type === "datetime" && sql.includes("<") && DATE.test(v.trim())) val = nextDay(v.trim()) + " 00:00:00";
    where.push("t." + sql); args.push(val);   // every filter starts with its column; t is the main table
  }
  const q = (url.searchParams.get("q") || "").trim();
  if (q && ["leads", "households"].includes(spec.table)) {
    const pk = phoneKey(q);
    if (pk) { where.push("(t.phone_key = ? OR t.secondary_phone_key = ?)"); args.push(pk, pk); }
    else {
      const like = `%${q.toLowerCase()}%`;
      where.push("(lower(t.firstname || ' ' || t.lastname) LIKE ? OR lower(coalesce(t.business_name, '')) LIKE ? OR lower(coalesce(t.email, '')) LIKE ?)");
      args.push(like, like, like);
    }
  }
  const limit = Math.min(MAX_LIMIT, Math.max(1, Number(url.searchParams.get("limit")) || 100));
  const page = Math.max(0, Number(url.searchParams.get("page")) || 0);
  const w = where.length ? " WHERE " + where.join(" AND ") : "";
  const order = spec.order.split(",").map((x) => "t." + x.trim()).join(", ");
  const [total, rows] = await db.batch([
    db.prepare(`SELECT count(*) AS n FROM ${spec.table} t${w}`).bind(...args),
    db.prepare(`SELECT ${selectOf(spec)} FROM ${spec.table} t ${joinOf(spec)}${w} ORDER BY ${order} LIMIT ? OFFSET ?`).bind(...args, limit, page * limit),
  ]);
  const totalCount = ((total.results || [])[0] || {}).n || 0;
  return json({ [spec.key]: (rows.results || []).map((r) => rowToApi(spec, r, lk)), totalCount, page, limit });
}
const selectOf = (spec) => "t.*" + (spec.joins ? ", " + spec.joins.select : "");
const joinOf = (spec) => (spec.joins ? spec.joins.sql + " " : "");
async function getOne(db, spec, id, lk) {
  const row = await db.prepare(`SELECT ${selectOf(spec)} FROM ${spec.table} t ${joinOf(spec)}WHERE t.id = ?`).bind(id).first();
  if (!row) return json({ error: `${spec.label} ${id} not found` }, 404);
  return json(rowToApi(spec, row, lk));
}
async function create(db, spec, body, me, lk) {
  const p = pick(spec, body, spec.create, true);
  if (p.error) return json({ error: p.error }, 400);
  const cols = withPhoneKeys(p.cols);
  const now = localStr();
  const hasCol = (c) => Object.values(spec.fields).some(([col]) => col === c);
  if (hasCol("create_date")) cols.create_date = now;
  if (hasCol("created_by")) cols.created_by = me.id;
  if (spec.table === "leads") {
    cols.last_activity_date = now;
    if (cols.workflow_stage_id) { cols.enter_stage_date = now; cols.workflow_id = lk.stageWorkflow.get(cols.workflow_stage_id) ?? cols.workflow_id ?? null; }
    if (cols.workflow_id && !lk.workflows.has(cols.workflow_id)) return json({ error: "workflowId: no such pipeline" }, 400);
    if (cols.workflow_stage_id && !lk.stages.has(cols.workflow_stage_id)) return json({ error: "workflowStageId: no such stage" }, 400);
    if (cols.lead_source_id && !lk.sources.has(cols.lead_source_id)) return json({ error: "leadSourceId: no such lead source" }, 400);
  }
  if (spec.table === "households") { cols.modify_date = now; cols.as_customer_date = cols.as_customer_date || now; }
  if (spec.table === "service_requests") {
    cols.modify_date = now; cols.modified_by = me.id;
    if (!lk.workflows.has(cols.workflow_id)) return json({ error: "workflowId: no such workflow" }, 400);
    if (cols.workflow_stage_id) {
      if (lk.stageWorkflow.get(cols.workflow_stage_id) !== cols.workflow_id) return json({ error: "workflowStageId: not a stage of that workflow" }, 400);
      cols.enter_stage_date = now;
    }
    cols.customer_type = cols.customer_type || (cols.household_id ? "customer" : cols.lead_id ? "lead" : null);
  }
  if (spec.table === "tasks") cols.customer_type = cols.household_id ? "customer" : cols.lead_id ? "lead" : cols.sr_id ? "serviceTicket" : null;
  if (spec.table === "quotes") cols.quote_date = cols.quote_date || now;
  if (spec.table === "policies") cols.modify_date = now;
  const keys = Object.keys(cols);
  const r = await db.prepare(`INSERT INTO ${spec.table} (${keys.join(", ")}) VALUES (${keys.map(() => "?").join(", ")})`)
    .bind(...keys.map((k) => cols[k])).run();
  const id = r.meta.last_row_id;
  const stmts = [eventStmt(db, me.email, spec.label, id, "create", null, p.api)];
  // A quote on a lead is a presented quote: the lead's quoteDate moves (daily.py's
  // first rule for households quoted) and the lead was worked.
  if (spec.table === "quotes") stmts.push(db.prepare("UPDATE leads SET quote_date = coalesce(quote_date, ?), last_activity_date = ? WHERE id = ?").bind(cols.quote_date, now, cols.lead_id));
  if (spec.table === "tasks" && cols.lead_id) stmts.push(db.prepare("UPDATE leads SET last_activity_date = ? WHERE id = ?").bind(now, cols.lead_id));
  await db.batch(stmts);
  return getOne(db, spec, id, lk);
}
async function update(db, spec, id, body, me, lk) {
  const row = await db.prepare(`SELECT * FROM ${spec.table} WHERE id = ?`).bind(id).first();
  if (!row) return json({ error: `${spec.label} ${id} not found` }, 404);
  const p = pick(spec, body, spec.edit, false);
  if (p.error) return json({ error: p.error }, 400);
  const cols = withPhoneKeys(p.cols);
  const { before, after } = changed(spec, row, cols);
  if (!Object.keys(after).length) return getOne(db, spec, id, lk);
  const now = localStr();
  if ("modify_date" in row) cols.modify_date = now;
  if ("modified_by" in row) cols.modified_by = me.id;
  if (spec.table === "leads") cols.last_activity_date = now;
  const keys = Object.keys(cols);
  await db.batch([
    db.prepare(`UPDATE ${spec.table} SET ${keys.map((k) => `${k} = ?`).join(", ")} WHERE id = ?`).bind(...keys.map((k) => cols[k]), id),
    eventStmt(db, me.email, spec.label, id, "update", before, after),
  ]);
  return getOne(db, spec, id, lk);
}

/* ---- notes ---------------------------------------------------------------- */
/** A lead's notes NEWEST FIRST, as AgencyZoom hands them (CLAUDE.md: the day's
    MOVE_STAGE notes arrive newest first), stage moves included. */
async function notesOf(db, parentCol, id) {
  const r = await db.prepare(`SELECT * FROM notes WHERE ${parentCol} = ? ORDER BY create_date DESC, id DESC`).bind(id).all();
  return json((r.results || []).map(noteToApi));
}
async function addNote(db, parentCol, id, body, me, origin = "person") {
  if (!body || typeof body !== "object") return json({ error: "a JSON object is expected" }, 400);
  const type = String(body.type || "NOTE").toUpperCase();
  if (!NOTE_TYPES.has(type)) return json({ error: `type: one of ${[...NOTE_TYPES].join(", ")}` }, 400);
  const text = typeof body.body === "string" ? body.body.trim() : "";
  if (!text && !(body.attachments && body.attachments.length)) return json({ error: "body is required" }, 400);
  if (text.length > 20000) return json({ error: "body: too long" }, 400);
  const attr = body.attr && typeof body.attr === "object" && !Array.isArray(body.attr) ? body.attr : {};
  const attachments = Array.isArray(body.attachments) ? body.attachments.slice(0, 20) : [];
  const [okDate, when] = checkValue("datetime", body.createDate || localStr());
  if (!okDate) return json({ error: "createDate: not a datetime" }, 400);
  const parent = await db.prepare(`SELECT id FROM ${parentCol === "lead_id" ? "leads" : parentCol === "household_id" ? "households" : "service_requests"} WHERE id = ?`).bind(id).first();
  if (!parent) return json({ error: "not found" }, 404);
  const r = await db.prepare(`INSERT INTO notes (${parentCol}, type, body, attr, attachments, origin, created_by, create_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
    .bind(id, type, text, JSON.stringify(attr), JSON.stringify(attachments), origin, me.id, when).run();
  const nid = r.meta.last_row_id;
  const stmts = [eventStmt(db, me.email, "note", nid, "create", null, { type, on: parentCol, id })];
  if (parentCol === "lead_id") stmts.push(db.prepare("UPDATE leads SET last_activity_date = max(coalesce(last_activity_date, ''), ?) WHERE id = ?").bind(when, id));
  if (parentCol === "sr_id") stmts.push(db.prepare("UPDATE service_requests SET modify_date = ?, modified_by = ? WHERE id = ?").bind(when, me.id, id));
  await db.batch(stmts);
  const row = await db.prepare("SELECT * FROM notes WHERE id = ?").bind(nid).first();
  return json(noteToApi(row), 201);
}

/* ---- actions ---------------------------------------------------------------- */
/** The MOVE_STAGE note in AgencyZoom's own wording -- "Lead <name> moved from
    <from> to <to> by <person> Comments: <why>" -- so live_contact.
    _move_stage_parts and pipelines.parse_move read Pantheon's moves exactly
    like AgencyZoom's. A lead never moved before reads from "New lead". */
function moveNote(lead, fromWhere, to, me, why) {
  const name = `${lead.firstname || ""} ${lead.lastname || ""}`.trim() || lead.business_name || `#${lead.id}`;
  return `Lead ${name} moved from ${fromWhere || "New lead"} to ${to} by ${me.name}${why ? ` Comments: ${why}` : ""}`;
}
/** Move a lead: body.to is "Pipeline | Stage" (a stage the lookups know) or an
    exit (pipelines.EXITS: Smart-Cycle, Dead, Sold). Writes the structured move
    AND the MOVE_STAGE note lead_history reads ("<from> to <to>"), the way
    AgencyZoom's own note reads, so pipelines.parse_move needs no change. */
async function moveLead(db, id, body, me, lk) {
  const lead = await db.prepare("SELECT * FROM leads WHERE id = ?").bind(id).first();
  if (!lead) return json({ error: `lead ${id} not found` }, 404);
  const to = String((body || {}).to || "").trim();
  const why = String((body || {}).why || "").trim().slice(0, 500);
  const dest = lk.whereOf.get(to);
  if (!dest && !EXITS.has(to)) return json({ error: `to: not a stage or exit the CRM knows (${to || "empty"})` }, 400);
  const fromWhere = lead.workflow_stage_id ? `${lk.workflows.get(lead.workflow_id)} | ${lk.stages.get(lead.workflow_stage_id)}` : (lead.exit || null);
  if (fromWhere === to) return json({ error: "the lead is already there" }, 409);
  const now = localStr();
  const text = moveNote(lead, fromWhere, to, me, why);
  const n = await db.prepare("INSERT INTO notes (lead_id, type, body, attr, origin, created_by, create_date) VALUES (?, 'MOVE_STAGE', ?, ?, 'person', ?, ?)")
    .bind(id, text, JSON.stringify({ from: fromWhere, to, lossReason: why || null }), me.id, now).run();
  const set = dest
    ? { workflow_id: dest.workflowId, workflow_stage_id: dest.stageId, enter_stage_date: now, exit: null, status: lead.status === 2 ? 2 : 0, loss_reason: null }
    : { workflow_id: null, workflow_stage_id: null, enter_stage_date: now, exit: to, status: to === "Dead" ? 3 : to === "Sold" ? 2 : lead.status, loss_reason: why || null };
  if (to === "Sold") set.sold_date = lead.sold_date || now;
  set.last_activity_date = now;
  const keys = Object.keys(set);
  await db.batch([
    db.prepare("INSERT INTO stage_moves (lead_id, from_where, to_where, loss_reason, moved_by, at, note_id) VALUES (?, ?, ?, ?, ?, ?, ?)")
      .bind(id, fromWhere, to, why || null, me.id, now, n.meta.last_row_id),
    db.prepare(`UPDATE leads SET ${keys.map((k) => `${k} = ?`).join(", ")} WHERE id = ?`).bind(...keys.map((k) => set[k]), id),
    eventStmt(db, me.email, "lead", id, "move", { where: fromWhere }, { where: to, why: why || null }),
  ]);
  return getOne(db, OBJECTS.leads, id, lk);
}
/** Mark a lead sold: status 2, soldDate now (CLAUDE.md: status 2 means sold and
    every sold lead carries a soldDate), and a household to hang the policies
    on -- body.householdId, else a new household from the lead. */
async function soldLead(db, id, body, me, lk) {
  const lead = await db.prepare("SELECT * FROM leads WHERE id = ?").bind(id).first();
  if (!lead) return json({ error: `lead ${id} not found` }, 404);
  if (lead.status === 2) return json({ error: "already sold" }, 409);
  const now = localStr();
  let hh = Number((body || {}).householdId) || lead.converted_household_id || null;
  if (hh) {
    const h = await db.prepare("SELECT id FROM households WHERE id = ?").bind(hh).first();
    if (!h) return json({ error: `household ${hh} not found` }, 404);
  } else {
    const r = await db.prepare(`INSERT INTO households (firstname, lastname, business_name, phone, phone_key, secondary_phone, secondary_phone_key,
      email, address, city, state, zip, assigned_to, as_customer_date, create_date, modify_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)`)
      .bind(lead.firstname, lead.lastname, lead.business_name, lead.phone, lead.phone_key, lead.secondary_phone, lead.secondary_phone_key,
        lead.email, lead.address, lead.city, lead.state, lead.zip, lead.assigned_to, now, now, now).run();
    hh = r.meta.last_row_id;
    await eventStmt(db, me.email, "household", hh, "create", null, { fromLead: id }).run();
  }
  const fromWhere = lead.workflow_stage_id ? `${lk.workflows.get(lead.workflow_id)} | ${lk.stages.get(lead.workflow_stage_id)}` : (lead.exit || null);
  const n = await db.prepare("INSERT INTO notes (lead_id, type, body, attr, origin, created_by, create_date) VALUES (?, 'MOVE_STAGE', ?, ?, 'person', ?, ?)")
    .bind(id, moveNote(lead, fromWhere, "Sold", me, ""), JSON.stringify({ from: fromWhere, to: "Sold" }), me.id, now).run();
  await db.batch([
    db.prepare("INSERT INTO stage_moves (lead_id, from_where, to_where, moved_by, at, note_id) VALUES (?, ?, 'Sold', ?, ?, ?)").bind(id, fromWhere, me.id, now, n.meta.last_row_id),
    db.prepare("UPDATE leads SET status = 2, sold_date = ?, converted_household_id = ?, workflow_id = NULL, workflow_stage_id = NULL, exit = 'Sold', enter_stage_date = ?, last_activity_date = ? WHERE id = ?")
      .bind(now, hh, now, now, id),
    eventStmt(db, me.email, "lead", id, "sold", { status: lead.status }, { status: 2, soldDate: now, convertedHouseholdId: hh }),
  ]);
  return getOne(db, OBJECTS.leads, id, lk);
}
async function completeTask(db, id, body, me, lk) {
  const t = await db.prepare("SELECT * FROM tasks WHERE id = ?").bind(id).first();
  if (!t) return json({ error: `task ${id} not found` }, 404);
  if (t.status === 1) return json({ error: "already completed" }, 409);
  const now = localStr();
  const stmts = [
    db.prepare("UPDATE tasks SET status = 1, complete_date = ?, completed_by = ? WHERE id = ?").bind(now, me.id, id),
    eventStmt(db, me.email, "task", id, "complete", { status: 0 }, { status: 1, completeDate: now }),
  ];
  const comment = String((body || {}).comment || "").trim();
  if (t.lead_id) stmts.push(db.prepare("INSERT INTO notes (lead_id, type, body, attr, origin, created_by, create_date) VALUES (?, 'TASK', ?, ?, 'person', ?, ?)")
    .bind(t.lead_id, `Task completed: ${t.title}${comment ? ` -- ${comment}` : ""}`, JSON.stringify({ taskId: id }), me.id, now),
    db.prepare("UPDATE leads SET last_activity_date = ? WHERE id = ?").bind(now, t.lead_id));
  await db.batch(stmts);
  return getOne(db, OBJECTS.tasks, id, lk);
}
/** Complete an SR on one of Frank's resolutions (CLAUDE.md: the only outcomes),
    with the closing note Athena reads. */
async function completeSr(db, id, body, me, lk) {
  const sr = await db.prepare("SELECT * FROM service_requests WHERE id = ?").bind(id).first();
  if (!sr) return json({ error: `SR ${id} not found` }, 404);
  if (sr.status === 2) return json({ error: "already completed" }, 409);
  const rid = Number((body || {}).resolutionId) || null;
  if (!rid || !lk.resolutions.has(rid)) return json({ error: "resolutionId: one of the resolutions the CRM knows is required" }, 400);
  const now = localStr();
  const note = String((body || {}).note || "").trim();
  const stmts = [
    db.prepare("UPDATE service_requests SET status = 2, complete_date = ?, completed_by = ?, resolution_id = ?, resolution_desc = ?, modify_date = ?, modified_by = ? WHERE id = ?")
      .bind(now, me.id, rid, lk.resolutions.get(rid), now, me.id, id),
    eventStmt(db, me.email, "SR", id, "complete", { status: sr.status }, { status: 2, completeDate: now, resolutionId: rid }),
  ];
  if (note) stmts.push(db.prepare("INSERT INTO notes (sr_id, household_id, lead_id, type, body, attr, origin, created_by, create_date) VALUES (?, ?, ?, 'NOTE', ?, ?, 'person', ?, ?)")
    .bind(id, sr.household_id, sr.lead_id, note, JSON.stringify({ resolutionId: rid }), me.id, now));
  await db.batch(stmts);
  return getOne(db, OBJECTS.srs, id, lk);
}

/* ---- search ----------------------------------------------------------------- */
/** Everything on a number (the pipeline's first question: "which lead did this
    RingCentral number belong to") or a name: leads, households and the open SRs
    on those households. */
async function search(db, url, lk) {
  const phone = url.searchParams.get("phone"), q = (url.searchParams.get("q") || "").trim();
  const pk = phoneKey(phone || q);
  let leads, hhs;
  if (pk) {
    [leads, hhs] = await db.batch([
      db.prepare("SELECT * FROM leads WHERE phone_key = ? OR secondary_phone_key = ? ORDER BY last_activity_date DESC LIMIT 50").bind(pk, pk),
      db.prepare("SELECT * FROM households WHERE phone_key = ? OR secondary_phone_key = ? ORDER BY modify_date DESC LIMIT 50").bind(pk, pk),
    ]);
  } else if (q.length >= 2) {
    const like = `%${q.toLowerCase()}%`;
    [leads, hhs] = await db.batch([
      db.prepare("SELECT * FROM leads WHERE lower(firstname || ' ' || lastname) LIKE ? OR lower(coalesce(business_name,'')) LIKE ? ORDER BY last_activity_date DESC LIMIT 50").bind(like, like),
      db.prepare("SELECT * FROM households WHERE lower(firstname || ' ' || lastname) LIKE ? OR lower(coalesce(business_name,'')) LIKE ? ORDER BY modify_date DESC LIMIT 50").bind(like, like),
    ]);
  } else return json({ error: "phone or q (2+ characters) is required" }, 400);
  const hhIds = (hhs.results || []).map((h) => h.id);
  let srs = { results: [] };
  if (hhIds.length) srs = await db.prepare(`SELECT * FROM service_requests WHERE status = 1 AND household_id IN (${hhIds.map(() => "?").join(",")}) ORDER BY create_date DESC`).bind(...hhIds).all();
  return json({
    key: pk, leads: (leads.results || []).map((r) => rowToApi(OBJECTS.leads, r, lk)),
    customers: (hhs.results || []).map((r) => rowToApi(OBJECTS.households, r, lk)),
    serviceTickets: (srs.results || []).map((r) => rowToApi(OBJECTS.srs, r, lk)),
  });
}
async function events(db, url) {
  const object = url.searchParams.get("object") || "", id = Number(url.searchParams.get("id"));
  if (!object || !id) return json({ error: "object and id are required" }, 400);
  const r = await db.prepare("SELECT * FROM events WHERE object = ? AND object_id = ? ORDER BY at DESC, id DESC LIMIT 200").bind(object, id).all();
  return json((r.results || []).map((e) => ({ id: e.id, at: e.at, who: e.who, action: e.action,
    before: e.before ? JSON.parse(e.before) : null, after: e.after ? JSON.parse(e.after) : null })));
}

/* ---- the Lists page's reads and writes ------------------------------------------- */
/** Frank's lists, every AgencyZoom entry with its place, and how much sits on
    each (leads / policies per source, leads per workflow and stage, SRs per
    workflow and category) -- six GROUP BY passes, so only the Lists page asks. */
async function listsPage(db, lk) {
  const t = await listTables(db);
  const byKind = listsByKind(t.lists);
  const mapOf = {};
  for (const m of t.map) mapOf[`${m.kind}:${m.az_id}`] = m;
  const counts = {};
  if (t.ready) {
    const [ls, ps, lw, lst, sw, sc] = await db.batch([
      db.prepare("SELECT lead_source_id AS k, count(*) AS n FROM leads GROUP BY lead_source_id"),
      db.prepare("SELECT lead_source_id AS k, count(*) AS n FROM policies GROUP BY lead_source_id"),
      db.prepare("SELECT workflow_id AS k, count(*) AS n FROM leads WHERE status = 0 GROUP BY workflow_id"),
      db.prepare("SELECT workflow_stage_id AS k, count(*) AS n FROM leads WHERE status = 0 GROUP BY workflow_stage_id"),
      db.prepare("SELECT workflow_id AS k, count(*) AS n FROM service_requests GROUP BY workflow_id"),
      db.prepare("SELECT category_id AS k, count(*) AS n FROM service_requests GROUP BY category_id"),
    ]);
    const toMap = (r) => new Map((r.results || []).map((x) => [x.k, x.n]));
    Object.assign(counts, { leadsBySource: toMap(ls), policiesBySource: toMap(ps), openLeadsByWorkflow: toMap(lw), openLeadsByStage: toMap(lst), srsByWorkflow: toMap(sw), srsByCategory: toMap(sc) });
  }
  const c = (m, k) => (m && m.get(k)) || 0;
  const place = (kind, id) => { const m = mapOf[`${kind}:${id}`]; return m ? { listId: m.list_id, detail: m.detail, placedBy: m.placed_by, placed: true } : { listId: null, detail: null, placedBy: null, placed: false }; };
  const [s, w, st, cat] = await db.batch([
    db.prepare("SELECT id, name, active FROM lead_sources ORDER BY name"),
    db.prepare("SELECT id, name, kind, active FROM workflows ORDER BY kind, name"),
    db.prepare("SELECT id, workflow_id, name, ord, active FROM stages ORDER BY workflow_id, ord, id"),
    db.prepare("SELECT id, name, active FROM service_categories ORDER BY name"),
  ]);
  const rows = (x) => (x && x.results) || [];
  const az = {
    sources: rows(s).map((x) => ({ id: x.id, name: x.name, active: !!x.active, ...place("source", x.id), leads: c(counts.leadsBySource, x.id), policies: c(counts.policiesBySource, x.id) })),
    workflows: rows(w).map((x) => ({ id: x.id, name: x.name, kind: x.kind, active: !!x.active, ...place("workflow", x.id), leads: c(counts.openLeadsByWorkflow, x.id), srs: c(counts.srsByWorkflow, x.id) })),
    stages: rows(st).map((x) => ({ id: x.id, workflowId: x.workflow_id, name: x.name, active: !!x.active, ...place("stage", x.id), leads: c(counts.openLeadsByStage, x.id) })),
    categories: rows(cat).map((x) => ({ id: x.id, name: x.name, active: !!x.active, ...place("category", x.id), srs: c(counts.srsByCategory, x.id) })),
  };
  // a stage of a workflow nobody placed, or of a service workflow, is not Unsorted: it waits on its workflow
  const salesWf = new Set(az.workflows.filter((x) => x.placed && x.kind === "sales").map((x) => x.id));
  for (const x of az.stages) x.waits = !salesWf.has(x.workflowId);
  const unsorted = az.sources.filter((x) => !x.placed).length + az.workflows.filter((x) => !x.placed).length
    + az.stages.filter((x) => !x.placed && !x.waits).length + az.categories.filter((x) => !x.placed).length;
  return json({ ready: t.ready, lists: { sources: byKind.source, pipelines: byKind.pipeline, service: byKind.service }, az, unsorted });
}
/** add / edit / order one of Frank's lists. */
async function listsWrite(db, body, me) {
  if (!body || typeof body !== "object") return json({ error: "a JSON object is expected" }, 400);
  const op = String(body.op || ""), kind = String(body.kind || "");
  if (!LIST_KINDS.has(kind)) return json({ error: "kind: source, pipeline, stage or service" }, 400);
  const t = await listTables(db);
  if (!t.ready) return json({ error: "the lists are not loaded yet (migration 0004 / the first sync)" }, 409);
  const mine = t.lists.filter((x) => x.kind === kind);
  const clean = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : null);
  if (op === "add") {
    const name = clean(body.name, 80);
    if (!name) return json({ error: "name is required" }, 400);
    if (mine.some((x) => x.name.toLowerCase() === name.toLowerCase() && (kind !== "stage" || x.parentId === Number(body.parentId)))) return json({ error: "that name is already on the list" }, 409);
    let parent = null, id;
    if (kind === "stage") {
      parent = Number(body.parentId);
      if (!t.lists.some((x) => (x.kind === "pipeline" || x.kind === "service") && x.id === parent)) return json({ error: "parentId: no such pipeline" }, 400);
      const sibs = mine.filter((x) => x.parentId === parent);
      id = Math.max(parent * 100, ...sibs.map((x) => x.id)) + 1;
    } else id = Math.max(0, ...mine.map((x) => x.id)) + 1;
    const ord = Math.max(0, ...mine.filter((x) => x.parentId === parent).map((x) => x.ord)) + 1;
    await db.batch([
      db.prepare("INSERT INTO lists (kind, id, name, parent_id, detail_label, meaning, ord, active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)")
        .bind(kind, id, name, parent, clean(body.detailLabel, 60), clean(body.meaning, 400), ord),
      eventStmt(db, me.email, "list", id, "create", null, { kind, name, parentId: parent }),
    ]);
    return json({ ok: true, id });
  }
  if (op === "edit") {
    const id = Number(body.id), cur = mine.find((x) => x.id === id);
    if (!cur) return json({ error: "no such entry" }, 404);
    const set = {}, before = {}, after = {};
    if ("name" in body) { const v = clean(body.name, 80); if (!v) return json({ error: "name cannot be empty" }, 400); set.name = v; }
    if ("detailLabel" in body) set.detail_label = clean(body.detailLabel, 60);
    if ("meaning" in body) set.meaning = clean(body.meaning, 400);
    if ("active" in body) set.active = body.active ? 1 : 0;
    const back = { name: "name", detail_label: "detailLabel", meaning: "meaning", active: "active" };
    for (const [c, v] of Object.entries(set)) { const k = back[c]; const was = k === "active" ? (cur.active ? 1 : 0) : cur[k]; if ((was ?? null) !== (v ?? null)) { before[k] = was ?? null; after[k] = v ?? null; } }
    if (!Object.keys(after).length) return json({ ok: true, id });
    const keys = Object.keys(set);
    await db.batch([
      db.prepare(`UPDATE lists SET ${keys.map((k) => `${k} = ?`).join(", ")} WHERE kind = ? AND id = ?`).bind(...keys.map((k) => set[k]), kind, id),
      eventStmt(db, me.email, "list", id, "update", { kind, ...before }, { kind, ...after }),
    ]);
    return json({ ok: true, id });
  }
  if (op === "order") {
    const ids = Array.isArray(body.ids) ? body.ids.map(Number) : [];
    if (!ids.length || ids.some((i) => !mine.some((x) => x.id === i))) return json({ error: "ids: entries of that list" }, 400);
    await db.batch([...ids.map((i, k) => db.prepare("UPDATE lists SET ord = ? WHERE kind = ? AND id = ?").bind(k + 1, kind, i)),
      eventStmt(db, me.email, "list", 0, "order", null, { kind, ids })]);
    return json({ ok: true });
  }
  return json({ error: "op: add, edit or order" }, 400);
}
/** Place an AgencyZoom entry under one of Frank's: list_map upsert, placed_by the email. */
async function listsPlace(db, body, me) {
  if (!body || typeof body !== "object") return json({ error: "a JSON object is expected" }, 400);
  const kind = String(body.kind || ""), azId = Number(body.azId);
  if (!MAP_KINDS.has(kind)) return json({ error: "kind: source, workflow, stage or category" }, 400);
  if (!Number.isInteger(azId) || azId <= 0) return json({ error: "azId is required" }, 400);
  const t = await listTables(db);
  if (!t.ready) return json({ error: "the lists are not loaded yet (migration 0004 / the first sync)" }, 409);
  const listId = body.listId == null || body.listId === "" ? null : Number(body.listId);
  if (listId === null && kind !== "category") return json({ error: "listId is required (only a category may follow its workflow)" }, 400);
  if (listId !== null) {
    const ok = { source: ["source"], workflow: ["pipeline", "service"], stage: ["stage"], category: ["service"] }[kind];
    if (!t.lists.some((x) => ok.includes(x.kind) && x.id === listId)) return json({ error: `listId: not a ${ok.join(" or ")} entry` }, 400);
  }
  const table = { source: "lead_sources", workflow: "workflows", stage: "stages", category: "service_categories" }[kind];
  const az = await db.prepare(`SELECT id FROM ${table} WHERE id = ?`).bind(azId).first();
  if (!az) return json({ error: `no AgencyZoom ${kind} ${azId}` }, 404);
  const detail = typeof body.detail === "string" ? body.detail.trim().slice(0, 120) || null : null;
  const was = t.map.find((m) => m.kind === kind && m.az_id === azId) || null;
  await db.batch([
    db.prepare("INSERT INTO list_map (kind, az_id, list_id, detail, placed_by) VALUES (?, ?, ?, ?, ?) ON CONFLICT(kind, az_id) DO UPDATE SET list_id = excluded.list_id, detail = excluded.detail, placed_by = excluded.placed_by")
      .bind(kind, azId, listId, detail, me.email),
    eventStmt(db, me.email, "list_map", azId, was ? "update" : "create", was ? { kind, listId: was.list_id, detail: was.detail } : null, { kind, listId, detail }),
  ]);
  return json({ ok: true });
}

/* ---- the route ----------------------------------------------------------------- */
async function readBody(request) {
  try { return await request.json(); } catch (_) { return null; }
}
/** /api/crm/<parts...>; `identityOf` is the Worker's (the verified Access email). */
export async function crm(request, env, identityOf, parts, url) {
  const me0 = identityOf(request, env);
  const person = personByEmail(me0.email);
  // staff.json's `crm`: Frank alone until further notice (Frank, 2026-10-06:
  // "all of this is available to only me until further notice").
  if (!person || !hasBoard(me0.email, "crm")) return json({ error: "not permitted" }, 403);
  const db = env.CRM;
  if (!db) return json({ error: "CRM is not configured", detail: "add the D1 binding CRM in wrangler.jsonc and apply site/crm/migrations" }, 503);
  const me = { email: me0.email, id: person.az_id || null, name: person.name };
  const get = request.method === "GET", post = request.method === "POST";
  const [head, id, sub] = parts;
  try {
    if (head === "lookups" && get && parts.length === 1) return json(await lookups(db));
    if (head === "events" && get && parts.length === 1) return events(db, url);
    if (head === "lists") {
      if (parts.length === 1 && get) return listsPage(db);
      if (parts.length === 1 && post) return listsWrite(db, await readBody(request), me);
      if (parts.length === 2 && id === "place" && post) return listsPlace(db, await readBody(request), me);
      return json({ error: "not found" }, 404);
    }
    const lk = await nameMaps(db);
    if (head === "search" && get && parts.length === 1) return search(db, url, lk);
    const spec = OBJECTS[head];
    if (!spec) return json({ error: "not found" }, 404);
    if (parts.length === 1) {
      if (get) return list(db, spec, url, lk);
      if (post) return create(db, spec, await readBody(request), me, lk);
    }
    const nid = /^\d{1,12}$/.test(id || "") ? Number(id) : null;
    if (!nid) return json({ error: "not found" }, 404);
    if (parts.length === 2) {
      if (get) return getOne(db, spec, nid, lk);
      if (post) return update(db, spec, nid, await readBody(request), me, lk);
    }
    if (parts.length === 3) {
      if (sub === "notes" && NOTE_PARENT[head]) {
        if (get) return notesOf(db, NOTE_PARENT[head], nid);
        if (post) return addNote(db, NOTE_PARENT[head], nid, await readBody(request), me);
      }
      if (head === "leads" && sub === "quotes") {
        if (get) { url.searchParams.set("leadId", String(nid)); return list(db, OBJECTS.quotes, url, lk); }
        if (post) return create(db, OBJECTS.quotes, { ...(await readBody(request) || {}), leadId: nid }, me, lk);
      }
      if (post && head === "leads" && sub === "move") return moveLead(db, nid, await readBody(request), me, lk);
      if (post && head === "leads" && sub === "sold") return soldLead(db, nid, await readBody(request), me, lk);
      if (post && head === "tasks" && sub === "complete") return completeTask(db, nid, await readBody(request), me, lk);
      if (post && head === "srs" && sub === "complete") return completeSr(db, nid, await readBody(request), me, lk);
    }
    return json({ error: "not found" }, 404);
  } catch (e) {
    return json({ error: "CRM error", detail: String(e && e.message || e).slice(0, 300) }, 500);
  }
}
