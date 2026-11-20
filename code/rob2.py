import pyreadstat, os, json, numpy as np, pandas as pd
from scipy.stats import spearmanr

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
INC={1:"<1.0",2:"1.0-2.0",3:"2.0-3.0",4:"3.0-4.0",5:"4.0-5.0",6:"5.0-6.0",7:"6.0+"}

print("=== PAPER A R-a: employed respondents only (DQ5==1), overnight & day by income ===")
def load(y,extra=()):
    use=[c for c in ["국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","BINC1","BAGE","DQ5","WT_DOM"]+list(extra) if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use); return d
d19=load("2019"); w19=d19["WT_DOM"].values.astype(float)
AG=sorted(d19["BAGE"].dropna().unique()); std={g: w19[d19["BAGE"].values==g].sum()/w19.sum() for g in AG}
rows=[]
for y in ("2019","2025"):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    emp=(d["DQ5"].values==1) if "DQ5" in d else np.ones(len(d),bool)
    for k,lab in INC.items():
        sel=(d["BINC1"].values==k)&emp
        if sel.sum()<200: continue
        rows.append(dict(year=int(y),band=lab,k=k,n=int(sel.sum()),
            night=w[sel&nt].sum()/w[sel].sum()*100, day=w[sel&dy].sum()/w[sel].sum()*100))
E=pd.DataFrame(rows); a=E[E.year==2019].set_index("k"); b=E[E.year==2025].set_index("k")
out=pd.DataFrame({"band":[INC[k] for k in a.index],
  "night_%chg":[round((b.loc[k,"night"]/a.loc[k,"night"]-1)*100,2) for k in a.index],
  "day_pp":   [round(b.loc[k,"day"]-a.loc[k,"day"],2) for k in a.index],
  "n2025":[int(b.loc[k,"n"]) for k in a.index]})
pd.set_option("display.width",200); print(out.to_string(index=False))

print("\n=== PAPER A R-b: with and without the 2018 wave (aggregate series) ===")
for y in sorted(meta):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    print(f"  {y}: overnight {w[nt].sum()/w.sum()*100:5.2f}  day {w[dy].sum()/w.sum()*100:5.2f}")
print("  note: 2018 is the only wave lacking BARA and has half the design sample; excluded from regional analysis only")

print("\n=== PAPER B R-c: Spearman, and coupling excluding small-cell regions ===")
S=pd.read_csv(os.path.join(D,"regional_std.csv"))
TB=pd.read_csv(OUT)
nmin=TB.groupby("Region")["n"].min()
S=S.merge(nmin.rename("n_min"),left_on="region",right_index=True)
rho_p=S.night_idx_std.corr(S.day_idx_std)
rho_s=spearmanr(S.night_idx_std,S.day_idx_std).statistic
print(f"  all 17 regions : Pearson {rho_p:.3f}   Spearman {rho_s:.3f}")
for cut in (1500,2000,2500):
    k=S[S.n_min>=cut]
    if len(k)>=8:
        print(f"  n_min >= {cut}: {len(k):2d} regions  Pearson {k.night_idx_std.corr(k.day_idx_std):.3f}  "
              f"Spearman {spearmanr(k.night_idx_std,k.day_idx_std).statistic:.3f}")
print(f"  smallest regions by min cell: {nmin.sort_values().head(4).to_dict()}")

print("\n=== PAPER B R-d: coupling computed wave by wave (vs 2019 base) ===")
P=TB.copy()
base=P[P.Wave==2019].set_index("Region")
for y in sorted(P.Wave.unique()):
    if y==2019: continue
    cur=P[P.Wave==y].set_index("Region")
    common=[r for r in cur.index if r in base.index]
    ni=[cur.loc[r,"Overnight"]/base.loc[r,"Overnight"]*100 for r in common]
    di=[cur.loc[r,"Day"]/base.loc[r,"Day"]*100 for r in common]
    print(f"  {y}: n={len(common)}  Pearson {np.corrcoef(ni,di)[0,1]:+.3f}  Spearman {spearmanr(ni,di).statistic:+.3f}")
