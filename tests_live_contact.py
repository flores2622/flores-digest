"""Regression fixtures: every 2026-08-27 case Frank adjudicated.

    python3 tests_live_contact.py

Reads the cached 2026-08-27 data under data/, so it costs nothing and needs no
network. Each case is a row Frank ruled on by name; the comment is his reason.
Run this before shipping anything that touches live_contact.is_live,
transcribe.classify or the evidence gathering.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import live_contact as lc
tx=json.load(open('data/transcripts_2026-08-27.json'))
rank={"live":4,"voicemail":3,"no answer":2,"unclear":1,"unknown":0}
bynum, livesecs = {}, {}
for v in tx.values():
    n=v.get('to')
    if not n: continue
    k=(v.get('producer'), n)
    if rank.get(v['class'],0)>rank.get(bynum.get(k),-1): bynum[k]=v['class']
    if v['class']=='live':
        livesecs[k]=max(livesecs.get(k,0), int(v.get('duration') or 0))
import day_calls
rows=day_calls.classify('2026-08-27')
def find(who,name):
    for r in rows.get(who,[]):
        if (r['lead_name'] or '').lower()==name.lower(): return r
CASES=[
 ("Sarahi Chin","Ricardo Perea",True ,"spoke-note beats stale 'Called No Answer'"),
 ("Sarahi Chin","Jose Garcia"  ,True ,"94s live recording beats 'Called no answer'"),
 ("Coral Barwick","Guadalupe Garcia",True,"113s two-way Spanish call"),
 ("Crystal Mango","John Hoeppner",False,"'Rachel Anderson' asserts nothing; VM"),
 ("Sarahi Chin","Juan Esquivel" ,False,"coaching script is not a note"),
 ("Coral Barwick","Nazzer Robles",False,"to-do list is not a note"),
 ("Crystal Mango","Kenneth Payne",True ,"wrong number IS a live contact"),
 ("Crystal Mango","Elizabeth Los",True ,"real write-up, keeps live"),
 ("Mike Olvera","Rosa Villegas"  ,False,"7s 'live' must not beat a negative"),
 ("Lorena Gonzalez","Marcia Jobe",False,"25s 'live' must not beat a negative"),
 ("Lorena Gonzalez","Rachelle Bailey",False,"9s 'live' must not beat a negative"),
 ("Crystal Mango","Patrick Tate"  ,True ,"unchanged control"),
 ("Mike Olvera","Robert Evans"    ,True ,"unchanged control"),
]
bad=0
for who,name,want,why in CASES:
    r=find(who,name)
    if not r: print(f"  ?? {name}: no row"); bad+=1; continue
    ev=lc.evidence(r['lead_id'],'2026-08-27',who)
    k=(who,r['number'])
    ok,basis=lc.is_live(ev,r['talk_seconds'],bynum.get(k),live_seconds=livesecs.get(k,0))
    flag="ok " if ok==want else "FAIL"
    if ok!=want: bad+=1
    print(f"  {flag} {name:24} got={str(ok):5} want={str(want):5} basis={basis:38} — {why}")
print(f"\n{'ALL FIXTURES PASS' if not bad else str(bad)+' FAILING'}")
sys.exit(1 if bad else 0)
