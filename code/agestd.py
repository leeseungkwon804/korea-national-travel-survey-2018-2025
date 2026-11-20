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
def load(y):
    use=[c for c in ["국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","BINC1","BAGE","WT_DOM"] if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use); return d
d19=load("2019"); w19=d19["WT_DOM"].values.astype(float)
AG=sorted(d19["BAGE"].dropna().unique())
std={g: w19[d19["BAGE"].values==g].sum()/w19.sum() for g in AG}
INC={1:"<1.0",2:"1.0-2.0",3:"2.0-3.0",4:"3.0-4.0",5:"4.0-5.0",6:"5.0-6.0",7:"6.0+"}

def astd(d,mask_out,sel,w,POS):
    s=0.0
    for g,sh in std.items():
        m=sel&(d["BAGE"].values==g)
        if w[m].sum()>0: s+= sh*(w[m&mask_out].sum()/w[m].sum())
    return s*100

rows=[]
for y in ("2019","2025"):
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    for k,lab in INC.items():
        sel=(d["BINC1"].values==k)
        if sel.sum()<200: continue
        rows.append(dict(year=int(y),band=lab,k=k,
            night_c=w[sel&nt].sum()/w[sel].sum()*100, day_c=w[sel&dy].sum()/w[sel].sum()*100,
            night_s=astd(d,nt,sel,w,POS),           day_s=astd(d,dy,sel,w,POS)))
t=pd.DataFrame(rows); pd.set_option("display.width",220)
a=t[t.year==2019].set_index("k"); b=t[t.year==2025].set_index("k")
out=pd.DataFrame({"band":[INC[k] for k in a.index],
  "night_crude_%":[(b.loc[k,"night_c"]/a.loc[k,"night_c"]-1)*100 for k in a.index],
  "night_std_%":  [(b.loc[k,"night_s"]/a.loc[k,"night_s"]-1)*100 for k in a.index],
  "day_crude_pp": [ b.loc[k,"day_c"]-a.loc[k,"day_c"] for k in a.index],
  "day_std_pp":   [ b.loc[k,"day_s"]-a.loc[k,"day_s"] for k in a.index]}).round(2)
print("=== 2019 -> 2025 change, crude vs age-standardised (to 2019 age structure) ===")
print(out.to_string(index=False))

print("\n=== age composition of the lowest two income bands ===")
for y in ("2019","2025"):
    d=load(y); w=d["WT_DOM"].values.astype(float)
    sel=np.isin(d["BINC1"].values,[1,2])
    sh=[w[sel&(d["BAGE"].values==g)].sum()/w[sel].sum()*100 for g in AG]
    print(f"  {y} low-income age shares (15-19,20s,30s,40s,50s,60s,70+): "+"  ".join(f"{v:5.1f}" for v in sh))
    sel7=(d["BINC1"].values==7)
    sh7=[w[sel7&(d["BAGE"].values==g)].sum()/w[sel7].sum()*100 for g in AG]
    print(f"  {y} high-income age shares                               : "+"  ".join(f"{v:5.1f}" for v in sh7))
