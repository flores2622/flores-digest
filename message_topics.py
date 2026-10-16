"""What a customer's texts and emails are ABOUT, read by the model: a sale or
service (Frank, 2026-10-16: "for the texts and emails rule, can we just
figure out what their responding to and decide if its for service or
sales?").

WHY. A number can be a customer's (or carry an open SR) and also hold a
producer's open lead. Who that conversation belongs to was decided by the
records and by who typed last (messages.service_people), and each rule
missed a case: Jose Renteria (10-13), a customer with Mike's open Life Cross
Sell lead texting Crystal about his renewal, sat on the sales page; the first
fix for him moved Sarahi's winback quotes on Lorena's old leads off it. What
the conversation is about settles both: a renewal draft, a deductible and a
mailing address are service; a quote, a new policy or a winback is a sale.

WHAT IS READ. Only those people -- a number that routes to service AND is in
the lead notes -- and only when someone typed in the reply window (the
customer, or a person at the agency): the window's messages and the few
before them that the customer was answering, with card numbers taken out
(messages.redact), and one line about the records on the number. The answer
is "sales", "service" or "unclear"; unclear, or no read, leaves the old
rules to decide.

COST. A paid step like renewal_notes.py: one call per batch of up to BATCH
conversations. Every read is kept by number and the text read (data/ plus an
R2 copy), so a conversation is paid for once; a checkpoint re-reads only a
person whose conversation grew since the last. Never delete the cache
casually.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data/message_topic_reads.json"
CACHE_R2_KEY = "cache/message_topic_reads.json"
BATCH = 20
CHOICES = ("sales", "service", "unclear")

SYSTEM = """You read the texts and emails between an insurance agency and one \
person, and say whether the conversation is SALES work or SERVICE work.

The person has records on both sides: they are a customer of the agency (or \
have a service request open) and also have a sales lead with a producer. \
The question is what THIS conversation is about -- above all, what the \
person is writing about or answering.

sales: buying insurance they do not have yet. A quote or a price for a new \
policy or a product the household does not have (home, auto, life, renters, \
umbrella, a boat, a motorcycle, a business); a winback (a former customer \
being quoted to come back); an appointment or call to go over a quote; \
signing, the first payment, ID cards or documents for a policy SOLD IN THE \
LAST 30 DAYS (the records line says when they became a customer); a reply \
to a sales or marketing message (a quote follow-up, a cross-sell offer).

service: a policy they already have. A renewal (its price, its draft date, \
what changed), a payment or a bill, a late or missed payment, ID cards, \
proof of insurance or documents for an existing policy, adding or removing \
a car or a driver on an existing policy, a change of address, phone or \
email, a deductible or coverage change, a claim, a cancellation, a refund. \
A rewrite or re-quote of a policy they already have -- a lower price for the \
same policy at its renewal, moving it to another carrier to keep them -- is \
service too: the agency keeps rewrites with the service department.

Rules:
- Judge by what is said, not by who said it or which records exist.
- Both in one conversation: a sale still being worked -- a quote or new \
policy the person is considering and has not said no to -- makes it sales, \
even when they also ask about a policy they have (the producer answers \
both). It is service when the person writes only about their existing \
policy, or has said no to the new one (no car to bundle, staying with the \
policy they have).
- A thank-you, an "ok" or a reaction answers whatever it replies to: judge \
the message before it.
- Messages marked automation are the agency's drips and reminders; a reply \
to one is about what the drip said.
- unclear: nothing in the messages says (a bare "call me", a name, a \
picture with no words, a wrong number).

Return ONLY a JSON object mapping each id to sales, service or unclear, \
e.g. {"6025551234": "service"}."""

BATCH_LEAD = "Each key below is a phone number and each value is the conversation to read.\n"


def _h(text):
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def load(log=print):
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except ValueError:
            return {}
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=CACHE_R2_KEY)["Body"].read()
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_bytes(body)
        log("  message topics: restored earlier reads from R2")
        return json.loads(body)
    except Exception:
        return {}


def save(cache, log=print):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=CACHE_R2_KEY, Body=CACHE_FILE.read_bytes(),
                       ContentType="application/json")
    except Exception as e:
        log(f"  message topics: R2 copy not saved ({type(e).__name__})")


def _ask(cs, model, chunk):
    """One batch, as renewal_notes._ask: thinking off, one retry with more
    room if it is cut off. Raises rather than return nothing, so a failed
    batch is never cached."""
    base = {"model": model, "system": SYSTEM,
            "messages": [{"role": "user", "content": BATCH_LEAD + json.dumps(chunk, ensure_ascii=False)}]}
    room = 20 * len(chunk) + 200
    think = {"thinking": {"type": "disabled"}}
    try:
        resp = cs._post(dict(base, max_tokens=room, **think))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        think = {}
        resp = cs._post(dict(base, max_tokens=room * 4))
    got = cs._extract(resp)
    if got is None:
        got = cs._extract(cs._post(dict(base, max_tokens=room * 4, **think)))
    if not isinstance(got, dict):
        raise ValueError("no JSON in response")
    return got


def _cache_key(key, text):
    return f"{key[-10:]}|{_h(text)}"


def read(convs, log=print, asker=None):
    """{key: "sales" | "service" | "unclear"} for these conversations
    ({key: text}), reading only the ones not already read. A key missing
    from the result was not read (no API key, a failed batch) -- the caller's
    old rules decide it, and a later run reads it. Never raises. `asker`
    stands in for the model in tests: chunk -> {key: choice}."""
    cache = load(log=log)
    want = {k: t for k, t in convs.items() if _cache_key(k, t) not in cache}
    if want:
        model = "test"
        if asker is None:
            try:
                import call_summary as cs
                if not cs._key():
                    raise RuntimeError("ANTHROPIC_API_KEY not set")
                model = cs.pick_model()
                asker = lambda chunk: _ask(cs, model, chunk)
            except Exception as e:
                log(f"  message topics: not read ({type(e).__name__}: {str(e)[:160]}) -- "
                    f"the records decide until a later run reads them")
        keys, n_read = list(want), 0
        for i in range(0, len(keys) if asker else 0, BATCH):
            ids = keys[i:i + BATCH]
            chunk = {k[-10:]: want[k] for k in ids}
            try:
                got = asker(chunk)
            except Exception as e:
                log(f"  message topics: batch not read ({type(e).__name__}: {str(e)[:160]})")
                continue
            for k in ids:
                v = str(got.get(k[-10:]) or "").strip().lower()
                cache[_cache_key(k, want[k])] = {"choice": v if v in CHOICES else "unclear", "model": model}
            n_read += len(ids)
        if n_read:
            save(cache, log=log)
            log(f"  message topics: read {n_read} conversation(s) with {model}")
    out = {}
    for k, t in convs.items():
        hit = cache.get(_cache_key(k, t))
        if hit:
            out[k] = hit["choice"]
    return out


# ---- the day's decision, for the Service Center ------------------------------
# messages.build decides who is whose; service_messages.build (later in the
# same night) reads it, so a person the sales page hands to service shows on
# the Service Center and one it keeps does not show on both.

def day_file(day):
    return ROOT / f"data/msg_topics_{day}.json"


def save_day(day, service, sales):
    """The numbers (last ten digits) messages.build gave to service, and the
    ones a read kept as sales although they route to service."""
    p = day_file(day)
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps({"day": day, "service": sorted({k[-10:] for k in service}),
                             "sales": sorted({k[-10:] for k in sales})}))


def load_day(day):
    """(service numbers, sales numbers), or None when the day has no file."""
    p = day_file(day)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except ValueError:
        return None
    return set(d.get("service") or ()), set(d.get("sales") or ())
