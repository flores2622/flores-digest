"""Load the contacts and linked accounts Frank showed on AgencyZoom's customer
screens (2026-10-14: Claudia A Gallardo, Celerino A. Gallardo, L.L.C., Norma
De Leon) into Pantheon's CRM, so the feature can be checked on real accounts.

    python3 crm_links_seed.py                 # check the households exist, print the plan
    python3 crm_links_seed.py --write         # write it to the CRM (D1)
    python3 crm_links_seed.py --sqlite out/x.db --write

AgencyZoom's API returns none of this (CRM.md, "Contacts and linked accounts"),
so it is typed from the screenshots, nothing more:
  * Claudia's account: Claudia A Gallardo (primary) and Celerino A Gallardo.
  * The LLC: Celerino Gallardo (primary) and Claudia A Gallardo (the same
    contact as on her own account); linked to Claudia's account.
  * Norma De Leon: Norma (primary), Melissa De la Torre, Norver LLC, Pricila De
    La Torre; linked to Nordell, Inc, Delato Corp, Los Choches LLC and Meli's Inc.
    The screens show each linked business under Norma with ONE email and phone;
    they are read as that business's primary contact (Nordell, Delato -> Norma;
    Los Choches -> Pricila; Meli's -> Melissa). Their other contacts were not on
    the screens -- add them on the account's page.
Safe to run again: a contact, a link or an event that exists is not added twice,
and an account that already has a primary keeps it. Nothing here reads AgencyZoom.
"""
import sys

import crm_import
import crm_tasks
import staff

q = crm_import.q
WHO = "Frank (from AgencyZoom's screens, crm_links_seed.py)"

# (household id, contacts [(first, middle, last, email, phone, primary)], linked household ids)
CLAUDIA = ("Claudia", "A", "Gallardo", "cgallardo72@gmail.com", "(928) 246-8408")
CELERINO_A = ("Celerino", "A", "Gallardo", "gallaale17@hotmail.com", "(928) 247-3314")
CELERINO_LLC = ("Celerino", "", "Gallardo", "maxxbuilders1@gmail.com", "(928) 247-3314")
NORMA = ("Norma", "", "De Leon", "deleon23norma@gmail.com", "(928) 261-8832")
MELISSA = ("Melissa", "", "De la Torre", "melissadlt622@gmail.com", "(928) 287-1446")
NORVER = ("Norver LLC", "", "", None, None)
PRICILA = ("Pricila", "", "De La Torre", "pricila10078942@gmail.com", "(928) 430-6825")

PLAN = [
    (22182068, [CLAUDIA, CELERINO_A], [37076394]),
    (37076394, [CELERINO_LLC, CLAUDIA], []),
    (32707089, [NORMA, MELISSA, NORVER, PRICILA], [18486934, 18486962, 23013236, 34780149]),
    (18486934, [NORMA], []),       # Nordell, Inc
    (18486962, [NORMA], []),       # Delato Corp
    (23013236, [PRICILA], []),     # Los Choches LLC
    (34780149, [MELISSA], []),     # Meli's Inc
]


def run(db, sql):
    return db.c.execute(sql) if db.sqlite else db.d1.execute(sql)


def match(c):
    f, m, l, e, _ = c
    return f"firstname = {q(f)} AND middlename IS {q(m or None)} AND lastname = {q(l)} AND email IS {q(e)}"


def statements(now):
    out = []
    for hh, contacts, links in PLAN:
        for first_contact, c in enumerate(contacts):
            f, m, l, e, p = c
            out.append(f"INSERT INTO contacts (firstname, middlename, lastname, email, phone, phone_key, create_date) "
                       f"SELECT {q(f)}, {q(m or None)}, {q(l)}, {q(e)}, {q(p)}, {q(crm_import.e164(p) if p else None)}, {q(now)} "
                       f"WHERE NOT EXISTS (SELECT 1 FROM contacts WHERE {match(c)});")
            out.append(f"INSERT OR IGNORE INTO household_contacts (household_id, contact_id, is_primary, added_at) "
                       f"SELECT {hh}, id, CASE WHEN EXISTS (SELECT 1 FROM household_contacts WHERE household_id = {hh}) THEN 0 ELSE 1 END, {q(now)} "
                       f"FROM contacts WHERE {match(c)} ORDER BY id LIMIT 1;")
        for other in links:
            a, b = min(hh, other), max(hh, other)
            out.append(f"INSERT OR IGNORE INTO household_links (household_a, household_b, added_at) VALUES ({a}, {b}, {q(now)});")
        out.append(f"INSERT INTO events (at, who, object, object_id, action, before, after) SELECT {q(now)}, {q(WHO)}, 'household', {hh}, 'contacts_seeded', NULL, "
                   f"{q('{\"contacts\": ' + str(len(contacts)) + ', \"links\": ' + str(len(links)) + '}')} "
                   f"WHERE NOT EXISTS (SELECT 1 FROM events WHERE object = 'household' AND object_id = {hh} AND action = 'contacts_seeded');")
    return out


def main(argv):
    sqlite = argv[argv.index("--sqlite") + 1] if "--sqlite" in argv else None
    db = crm_tasks.connect(sqlite)
    if db is None:
        sys.exit("no CRM to write to")
    ids = sorted({hh for hh, _, links in PLAN for hh in [hh, *links]})
    have = {r["id"]: r for r in db.query(f"SELECT id, firstname, lastname, business_name FROM households WHERE id IN ({', '.join(map(str, ids))})")}
    missing = [i for i in ids if i not in have]
    for i in ids:
        r = have.get(i)
        print(f"  {i}  {(r['business_name'] or (r['firstname'] + ' ' + r['lastname'])).strip() if r else 'NOT IN THE CRM'}")
    if missing:
        sys.exit(f"{len(missing)} accounts are not in the CRM yet ({missing}) -- let the nightly mirror run first")
    if "--write" not in argv:
        print(f"{len(statements(''))} statements ready; add --write to apply them")
        return
    now = staff.now().strftime("%Y-%m-%d %H:%M:%S")
    for s in statements(now):
        run(db, s)
    if sqlite:
        db.c.commit()
    n = db.query("SELECT (SELECT count(*) FROM contacts) AS c, (SELECT count(*) FROM household_contacts) AS hc, (SELECT count(*) FROM household_links) AS l")[0]
    print(f"done: {n['c']} contacts, {n['hc']} contact-on-account rows, {n['l']} links in the CRM")


if __name__ == "__main__":
    main(sys.argv[1:])
