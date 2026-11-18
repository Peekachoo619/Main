import sys,wave,numpy as np,runpy,glob
C={}
def ld(c):
    if c not in C:
        w=wave.open(f'w/{c}.wav');C[c]=(w.getframerate(),np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768)
    return C[c]
for f in (sys.argv[1:] or sorted(glob.glob('ads/*.py'))):
    c=runpy.run_path(f);print(f)
    for i,L in enumerate(c['LINES']):
        sr,a=ld(L['clip']);t0,t1=L['win'];p=0.4;n=int(0.05*sr)
        seg=a[int((t0-p)*sr):int((t1+p)*sr)];k=len(seg)//n
        db=20*np.log10(np.sqrt((seg[:k*n].reshape(k,n)**2).mean(1))+1e-9)
        s="".join('#' if x>-24 else '+' if x>-30 else '.' if x>-40 else ' ' for x in db)
        print(f"{i:2d} {t0:7.2f} {s[:8]}|{s[8:-8]}|{s[-8:]}")
