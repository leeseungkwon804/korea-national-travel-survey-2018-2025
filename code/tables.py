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
MAP={11:1,21:2,22:3,23:4,24:5,25:6,26:7,29:8,31:9,32:10,33:11,34:12,35:13,36:14,37:15,38:16,39:17}
SIDO=["Seoul","Busan","Daegu","Incheon","Gwangju","Daejeon","Ulsan","Sejong","Gyeonggi",
      "Gangwon","Chungbuk","Chungnam","Jeonbuk","Jeonnam","Gyeongbuk","Gyeongnam","Jeju"]
def load(y,extra=()):
    use=list(dict.fromkeys(["WT_DOM","BAGE","BSEX","BEDU","BINC1","BARA",
        "국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","국내_월별여행경험_관광전체"]+list(extra)))
    use=[c for c in use if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use)
    if y=="2019" and "BARA" in d:
        d["BARA"]=[MAP.get(int(x),np.nan) if not np.isnan(x) else np.nan for x in d["BARA"].values]
    return d
ys=sorted(meta)

# ---- Table 1 (both papers): sample and respondent characteristics by wave
rows=[]
for y in ys:
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    r={"Wave":y,"n":len(d)}
    r["Female %"]=round(w[d["BSEX"].values==2].sum()/w.sum()*100,1) if "BSEX" in d else None
    r["Aged 60+ %"]=round(w[d["BAGE"].values>=6].sum()/w.sum()*100,1)
    r["Tertiary educ %"]=round(w[d["BEDU"].values==4].sum()/w.sum()*100,1) if "BEDU" in d else None
    r["Income <2.0m %"]=round(w[np.isin(d["BINC1"].values,[1,2])].sum()/w.sum()*100,1)
    r["Leisure particip. %"]=round(w[d["국내_월별여행경험_관광전체"].values==POS].sum()/w.sum()*100,2)
    r["Overnight %"]=round(w[d["국내_월별여행경험_관광숙박"].values==POS].sum()/w.sum()*100,2)
    r["Day %"]=round(w[d["국내_월별여행경험_관광당일"].values==POS].sum()/w.sum()*100,2)
    rows.append(r)
T1=pd.DataFrame(rows)
T1.to_csv(os.path.join(O,"Table1_sample_by_wave.csv"),index=False)
print("=== Table 1: sample and characteristics by wave ===")
print(T1.to_string(index=False))

# ---- Table 2 (Paper A): participation by wave, product, income band
INC={1:"<1.0",2:"1.0-2.0",3:"2.0-3.0",4:"3.0-4.0",5:"4.0-5.0",6:"5.0-6.0",7:"6.0+"}
rows=[]
for y in ys:
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    for k,lab in INC.items():
        sel=(d["BINC1"].values==k)
        if sel.sum()<200: continue
        rows.append(dict(Wave=y,Band=lab,n=int(sel.sum()),
            Overnight=round(w[sel&nt].sum()/w[sel].sum()*100,2),
            Day=round(w[sel&dy].sum()/w[sel].sum()*100,2)))
T2=pd.DataFrame(rows)
T2.to_csv(os.path.join(O,"Table2_participation_by_income_wave.csv"),index=False)
print(f"\n=== Table 2: {len(T2)} rows written (wave x income band x product) ===")
print(T2.head(8).to_string(index=False))

# ---- Table B2 (Paper B): regional panel
rows=[]
for y in ys:
    if "BARA" not in meta[y]["cols"]: continue
    d=load(y); w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    b=np.array(d["BARA"].values,dtype=float)
    for i,nm in enumerate(SIDO,start=1):
        sel=(b==i)
        if w[sel].sum()<=0: continue
        rows.append(dict(Wave=y,Region=nm,n=int(sel.sum()),
            Overnight=round(w[sel&nt].sum()/w[sel].sum()*100,2),
            Day=round(w[sel&dy].sum()/w[sel].sum()*100,2)))
TB=pd.DataFrame(rows)
TB.to_csv(os.path.join(O,"TableB2_regional_panel.csv"),index=False)
print(f"\n=== Table B2: {len(TB)} rows (wave x region x product) ===")
print(TB.head(6).to_string(index=False))

# ---- Table B3: resilience observed vs standardised + ageing
S=pd.read_csv(os.path.join(D,"regional_std.csv"))
S.to_csv(os.path.join(O,"TableB3_resilience_standardised.csv"),index=False)
print(f"\n=== Table B3 written: {len(S)} regions ===")
print(S.head(5).to_string(index=False))
