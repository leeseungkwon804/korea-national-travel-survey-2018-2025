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
SIDO=["Seoul","Busan","Daegu","Incheon","Gwangju","Daejeon","Ulsan","Sejong","Gyeonggi",
      "Gangwon","Chungbuk","Chungnam","Jeonbuk","Jeonnam","Gyeongbuk","Gyeongnam","Jeju"]
MAP2019={11:1,21:2,22:3,23:4,24:5,25:6,26:7,29:8,31:9,32:10,33:11,34:12,35:13,36:14,37:15,38:16,39:17}
rows=[]
for y in sorted(meta):
    if "BARA" not in meta[y]["cols"]: 
        print(f"{y}: no BARA, skipped"); continue
    use=["BARA","WT_DOM","국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일"]
    use=[c for c in use if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use)
    b=d["BARA"].values.astype(float)
    if y=="2019": b=np.array([MAP2019.get(int(x),np.nan) if not np.isnan(x) else np.nan for x in b])
    w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    for i,nm in enumerate(SIDO,start=1):
        sel=(b==i)
        if w[sel].sum()<=0: continue
        rows.append(dict(year=int(y),region=nm,
            night=round(w[sel&nt].sum()/w[sel].sum()*100,2),
            day  =round(w[sel&dy].sum()/w[sel].sum()*100,2), n=int(sel.sum())))
t=pd.DataFrame(rows); pd.set_option("display.width",250)
piv_n=t.pivot(index="region",columns="year",values="night").reindex(SIDO)
piv_d=t.pivot(index="region",columns="year",values="day").reindex(SIDO)
print("=== OVERNIGHT leisure participation by region of residence (weighted %) ===")
print(piv_n.to_string())
print("\n=== DAY-trip leisure participation by region of residence (weighted %) ===")
print(piv_d.to_string())
res=pd.DataFrame({"night_2019":piv_n[2019],"night_2025":piv_n[2025],
                  "day_2019":piv_d[2019],"day_2025":piv_d[2025]})
res["night_idx"]=(res.night_2025/res.night_2019*100).round(1)
res["day_idx"]=(res.day_2025/res.day_2019*100).round(1)
res=res.sort_values("night_idx")
print("\n=== resilience index, 2019 = 100 ===")
print(res[["night_2019","night_2025","night_idx","day_2019","day_2025","day_idx"]].to_string())
print(f"\nnight_idx: min={res.night_idx.min()} max={res.night_idx.max()} spread={res.night_idx.max()-res.night_idx.min():.1f}")
print(f"corr(night_idx, day_idx) = {res.night_idx.corr(res.day_idx):.3f}")
t.to_csv(os.path.join(D,"regional_panel.csv"),index=False); res.to_csv(os.path.join(D,"regional_resilience.csv"))
