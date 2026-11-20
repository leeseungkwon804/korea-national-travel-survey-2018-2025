import pyreadstat, os, json, numpy as np, pandas as pd

import os
# Paths are read from the environment so the code is portable.
#   NTS_DATA : directory holding the extracted SPSS files (YYYY_domestic.sav)
#   NTS_OUT  : directory for tables and figures
D   = os.environ.get("NTS_DATA", "./data")
OUT = os.environ.get("NTS_OUT",  "./outputs")
OA  = os.path.join(OUT, "paperA_figs")
OB  = os.path.join(OUT, "paperB_figs")
os.makedirs(OA, exist_ok=True); os.makedirs(OB, exist_ok=True)

meta=json.load(open(os.path.join(D,"_meta_domestic.json")))
LOW=[1,2]; HIGH=[7]
def load(y):
    use=[c for c in ["국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","BINC1","BAGE","WT_DOM"] if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use); return d

print("=== R1: weighted vs unweighted, overnight participation by income group ===")
for y in ("2019","2025"):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); inc=d["BINC1"].values
    lo=np.isin(inc,LOW); hi=np.isin(inc,HIGH)
    print(f"  {y}  low  W={w[lo&nt].sum()/w[lo].sum()*100:5.2f}  U={nt[lo].mean()*100:5.2f} |"
          f"  high W={w[hi&nt].sum()/w[hi].sum()*100:5.2f}  U={nt[hi].mean()*100:5.2f}")

print("\n=== R2: age-standardised to 2019 age structure, overnight by income group ===")
d19=load("2019"); w19=d19["WT_DOM"].values.astype(float)
std={g: w19[d19["BAGE"].values==g].sum()/w19.sum() for g in sorted(d19["BAGE"].dropna().unique())}
for y in ("2019","2025"):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); inc=d["BINC1"].values
    for lab,sel in (("low",np.isin(inc,LOW)),("high",np.isin(inc,HIGH))):
        crude=w[sel&nt].sum()/w[sel].sum()*100
        s=0.0
        for g,sh in std.items():
            m=sel&(d["BAGE"].values==g)
            if w[m].sum()>0: s+= sh*(w[m&nt].sum()/w[m].sum())
        print(f"  {y} {lab:<5} crude={crude:5.2f}  age-std={s*100:5.2f}")

print("\n=== R3: income non-response (code 99) share by wave ===")
for y in sorted(meta):
    d=load(y); w=d["WT_DOM"].values.astype(float)
    nr=(d["BINC1"].values==99)
    print(f"  {y}: non-response {nr.mean()*100:5.2f}% (unweighted)  n={nr.sum():,}")

print("\n=== R4: ratio high/low overnight participation, all 8 waves ===")
for y in sorted(meta):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); inc=d["BINC1"].values
    lo=np.isin(inc,LOW); hi=np.isin(inc,HIGH)
    a=w[lo&nt].sum()/w[lo].sum()*100; b=w[hi&nt].sum()/w[hi].sum()*100
    print(f"  {y}: low={a:5.2f}  high={b:5.2f}  ratio={b/a:4.2f}")
