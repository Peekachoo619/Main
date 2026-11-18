import sys,json,re,runpy,difflib,glob
n=lambda s:re.sub(r"[^a-z0-9 ]","",s.lower().replace("-"," ")).split()
for f in sorted(glob.glob('ads/*.py')):
    c=runpy.run_path(f)
    for i,L in enumerate(c['LINES']):
        W=json.load(open(f"w/{L['clip']}.json"));t0,t1=L['win']
        inw=[x for x in W if x['e']>t0+0.05 and x['s']<t1-0.05]
        h=n(" ".join(x['w'] for x in inw));s=n(L['text'])
        r=difflib.SequenceMatcher(None,s,h).ratio()
        edge=f"first {inw[0]['w']}@{inw[0]['s']:.2f}-{inw[0]['e']:.2f} last {inw[-1]['w']}@{inw[-1]['s']:.2f}-{inw[-1]['e']:.2f}" if inw else "NONE"
        if r<0.93 or len(h)!=len(s): print(f"{f} L{i} {L['win']} r={r:.2f}\n  want: {' '.join(s)}\n  heard: {' '.join(h)}\n  {edge}")
