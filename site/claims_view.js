/* Claims a viewer may see (Frank, 2026-10-02: "only the ops team should see
 * the not licensed card"). A claim opened by, or assigned to, someone not
 * licensed is flagged by claims.py; those flags reach only the ops team
 * (staff.json's `roleplay_history`, rpScope.all). Everyone else gets the same
 * claims with the flags taken off: no `flags` list, no `problems` or
 * `licensed` on a row. Used by the Service Center route and by Coeus. */
export function claimsForViewer(doc, ops) {
  if (ops || !doc || !doc.claims) return doc;
  const strip = (rs) => (rs || []).map((r) => { const { problems, licensed, ...rest } = r; return rest; });
  const c = doc.claims;
  doc.claims = Object.assign({}, c, { flags: [], opened: strip(c.opened), completed: strip(c.completed),
    open: c.open == null ? c.open : strip(c.open) });
  return doc;
}
