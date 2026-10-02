"""The Service Playbook -- Amanda's (head of service), as Athena works from it
(Frank, 2026-09-28: "this is the playbook she built with the duties,
responsibilities, and culture she wants. Teach Athena this and build the
digest to be focused on their own roles and responsibilities").

Everything here is her document, not ours: the roles, who handles what, the
note standard and the daily checklist. service_audit.py reads each completed
SR against it; the Service Center's By Role cards show each person the
measures of their own role. Change the playbook here, and only here.

    Service Lead          Amanda Torricellas
    Service Team Member   Crystal Mango (hybrid: service and sales)
    Front Desk            Debbie Aguilera
"""

PURPOSE = ("The Service Team is responsible for making sure our clients receive timely, "
           "knowledgeable, and professional service while keeping the agency organized and "
           "moving efficiently. Our goal is not for one person to handle everything. Our goal is "
           "for everyone to know their role, take ownership of their work, and work together to "
           "keep things moving.")
STANDARD = "Listen → Understand → Handle → Document → Follow Up"
CLIENT_SHOULD_FEEL = ["Heard", "Helped", "Confident that their request is being handled"]

ROLES = {
    "lead": {
        "title": "Service Lead",
        "primary": "Oversight, delegation, complex service, training, and keeping the service department moving.",
        "responsibilities": [
            "Monitor the overall service workload", "Delegate work appropriately",
            "Handle complex or sensitive service issues", "Handle Spanish-speaking service clients",
            "Handle more involved policy changes and coverage questions", "Review renewals and coverage requests",
            "Open and work claims (licensed reps only)",
            "Monitor missed calls, texts, faxes, and pending tasks", "Audit service notes and follow-up",
            "Train and support service team members", "Identify bottlenecks and redistribute work",
            "Step in when a team member needs assistance", "Escalate unresolved issues when necessary",
        ],
        "expectation": ("The Service Lead is not the default person for every service request. The goal is "
                        "to delegate and support the team, not become the team's backlog."),
    },
    "member": {
        "title": "Service Team Member",
        "primary": "Independently handle day-to-day policy service and keep assigned work moving.",
        "responsibilities": [
            "Handle routine policy service requests", "Answer policy questions", "Process policy changes",
            "Assist with billing/service questions", "Follow up on outstanding items",
            "Handle vehicle and driver changes", "Assist with lienholder/mortgagee changes",
            "Handle document and ID card requests", "Review renewal questions",
            "Open and work claims (licensed reps only)", "Maintain accurate account notes",
            "Complete assigned tasks", "Identify opportunities that should be passed to a producer",
            "Ask for help when an issue is outside their knowledge or authority",
        ],
        "expectation": ("If you can handle it, handle it. Do not pass routine work to another team member "
                        "simply because you are unsure. First check the account, policy, notes, and "
                        "available resources."),
    },
    "front_desk": {
        "title": "Service Support / Front Desk",
        "primary": ("Be the initial impression of the agency, assist with basic billing needs, and make "
                    "sure clients get to the right person."),
        "responsibilities": [
            "Answer incoming calls", "Greet walk-in clients", "Assist with basic billing questions",
            "Identify what the client needs", "Route clients appropriately", "Assign service requests",
            "Take a claim call to a licensed rep (Amanda or Crystal) -- the Front Desk does not open claims",
            "Monitor account alerts", "Handle NOCs and designated administrative tasks",
            "Make sure messages and tasks are assigned correctly",
        ],
        "expectation": ("The Front Desk does not need to solve every service issue. The goal is to identify "
                        "the need and confidently get the client to the right person."),
    },
}
ROLE_OF = {"Amanda Torricellas": "lead", "Crystal Mango": "member", "Debbie Aguilera": "front_desk"}
# Who sells (Frank, 2026-09-28: "Crystal is a hybrid position and also sells so
# she can do the opportunity herself, amanda as well. Debbie is the only one
# that would identify and pass to any producer"). The playbook's "identify
# opportunities that should be passed to a producer" is Debbie's; Crystal and
# Amanda work the opportunity themselves -- a quote, a lead, or passing it on.
SELLS = {"Amanda Torricellas", "Crystal Mango"}

# Who handles what -- the playbook's table, as the request types an SR is
# read into (service_audit.py). Owner: "service" (Front Desk or any Service
# Team member), "lead" (Service Lead / Producer), "producer", "frank".
REQUEST_TYPES = {
    "basic_billing": ("Basic billing question", "front_desk"),
    "documents": ("Policy documents", "service"),
    "id_cards": ("ID cards", "service"),
    "address_change": ("Address change", "service"),
    "vehicle_change": ("Vehicle change", "service"),
    "driver_change": ("Driver change", "service"),
    "lienholder_change": ("Lienholder/mortgagee change", "service"),
    "routine_change": ("Routine policy change", "service"),
    "renewal_question": ("Renewal question", "service"),
    "noc": ("NOC / administrative", "front_desk"),
    "complex_coverage": ("Complex coverage question", "lead"),
    "unresolved_issue": ("Unresolved service issue", "lead"),
    "sales_opportunity": ("New business / cross-sell / requote / new coverage", "producer"),
    "owner_escalation": ("Issue requiring owner/producer escalation", "frank"),
    "cancellation": ("Cancellation", "service"),
    # Claims are opened and worked by a licensed rep only -- of the service
    # team Amanda or Crystal, plus the ops team (Frank, 2026-10-02: "Debbie is
    # not licensed, she cannot open claims moving forward"). claims.py flags a claim SR anyone else opens.
    "claim": ("Claim", "licensed"),
    "other": ("Other", "service"),
}
ROUTINE = {k for k, (_, owner) in REQUEST_TYPES.items() if owner in ("service", "front_desk")}
from claims import LICENSED_NAMES as LICENSED      # who may open and work a claim
WHEN_IN_DOUBT = "When in doubt, start with the Service Team. We determine where the request needs to go."

# A note should answer these (Account & Note Standards).
NOTE_PARTS = {
    "who": "Who -- who contacted us or was contacted",
    "what": "What -- what they needed",
    "why": "Why -- the reason behind it",
    "outcome": "Outcome -- what was done or decided",
    "next_step": "Next step -- what happens next, or that nothing more is needed",
}
GOOD_NOTE = ("Client called regarding upcoming renewal increase. Reviewed policy changes and discussed "
             "deductible options. Client wants to keep current coverage. No changes made.")
VAGUE_NOTE = "Talked to client about renewal."

SERVICE_VS_SALES = ("Service first. Opportunity second. We don't force a sales conversation into every "
                    "interaction, but we also don't miss opportunities that are naturally presented to us. "
                    "(\"I'm adding a new vehicle\" -- handle the change, and see whether the household "
                    "could be reviewed or another policy added. \"We're buying a house\" -- handle the "
                    "need, and make sure the home opportunity gets to a producer.)")

COMMUNICATION = {
    "be": ["Warm", "Clear", "Confident", "Solution-focused"],
    "avoid": ["I don't know.", "That's not my job.", "You'll have to call someone else.", "I think...",
              "I'm not sure."],
    "instead": ["Let me take a look at that for you.", "I can help you with that.",
                "Let me check on that and I'll get back to you.", "I'll get you to the right person.",
                "Let me review the account first so I can give you the correct answer."],
}

PRIORITY = ["Time-sensitive items", "Client callbacks", "Pending items preventing a policy from moving forward",
            "Older outstanding tasks", "Routine requests"]

CHECKLIST = {
    "start": ["Check missed calls", "Check texts", "Check emails", "Review tasks", "Review urgent/pending items",
              "Identify follow-ups due today"],
    "during": ["Answer/return calls", "Work service requests", "Complete assigned tasks", "Document conversations",
               "Follow up on pending items", "Route sales opportunities", "Ask for help when needed",
               "Help teammates when available"],
    "end": ["Review unfinished tasks", "Complete required notes", "Return priority calls",
            "Make sure urgent items have a next step", "Communicate anything that needs to carry over"],
}

EXPECTATIONS = {
    "Ownership": "If you take the request, own it until it is resolved or properly handed off.",
    "Communication": "Don't let someone else discover that a client has been waiting.",
    "Documentation": "If it isn't documented, the next person doesn't know what happened.",
    "Follow-Through": "Don't make the client chase us for an answer.",
    "Teamwork": "We help each other. We do not operate as individual islands.",
    "Accountability": "Different responsibilities do not mean different levels of importance.",
    "Growth": "Ask questions. Learn from mistakes. Become more independent over time.",
}
CLOSING = ("We don't all have to do the same job, but we all have to do our part. We answer. We listen. "
           "We solve. We document. We follow up. We communicate. We help each other.")


def prompt_block():
    """The playbook, compact, for a model reading service notes."""
    types = "\n".join(f"  {k}: {label} (handled by: {owner})" for k, (label, owner) in REQUEST_TYPES.items())
    parts = "\n".join(f"  {k}: {v}" for k, v in NOTE_PARTS.items())
    return f"""THE AGENCY'S SERVICE PLAYBOOK (written by the head of service):
Standard: {STANDARD}. Every client should feel heard, helped, and confident their request is being handled.

Who handles what -- request types:
{types}
{WHEN_IN_DOUBT}

Note standard -- a note should answer:
{parts}
Good note: "{GOOD_NOTE}"
Too vague: "{VAGUE_NOTE}"
A good note lets the next team member pick up where you left off without asking the client to repeat themselves.

Service vs. sales: {SERVICE_VS_SALES}"""


def as_doc():
    """The playbook as the board reads it (each service day's `playbook`)."""
    return {"purpose": PURPOSE, "standard": STANDARD, "roles": ROLES, "role_of": ROLE_OF,
            "request_types": {k: list(v) for k, v in REQUEST_TYPES.items()}, "routine": sorted(ROUTINE),
            "sells": sorted(SELLS), "licensed": sorted(LICENSED),
            "when_in_doubt": WHEN_IN_DOUBT, "note_parts": NOTE_PARTS, "good_note": GOOD_NOTE,
            "vague_note": VAGUE_NOTE, "service_vs_sales": SERVICE_VS_SALES, "communication": COMMUNICATION,
            "priority": PRIORITY, "checklist": CHECKLIST, "expectations": EXPECTATIONS, "closing": CLOSING}
