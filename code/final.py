import pyreadstat, pandas as pd, numpy as np, os, json

import os
# Paths are read from the environment so the code is portable.
#   NTS_DATA : directory holding the extracted SPSS files (YYYY_domestic.sav)
#   NTS_OUT  : directory for tables and figures
D   = os.environ.get("NTS_DATA", "./data")
OUT = os.environ.get("NTS_OUT",  "./outputs")
OA  = os.path.join(OUT, "paperA_figs")
OB  = os.path.join(OUT, "paperB_figs")
os.makedirs(OA, exist_ok=True); os.makedirs(OB, exist_ok=True)

meta = json.load(open(os.path.join(D,"_meta_domestic.json")))
OFFV = {"dom":"국내_월별여행경험_국내전체","tour":"국내_월별여행경험_관광전체","etc":"국내_월별여행경험_기타전체"}
CNT  = {"tour":"국내_A_여행횟수_관광전체","etc":"국내_A_여행횟수_기타전체","dom":"국내_A_여행횟수_국내전체"}

def wp(mask, w):
    """weighted proportion (%) and SE (%) ignoring clustering (Taylor linearisation)."""
    y = mask.astype(float); W = w.sum(); p = (w*y).sum()/W
    var = (w**2 * (y-p)**2).sum() / W**2
    return p*100, np.sqrt(var)*100

def wmean(x, w, mask=None):
    if mask is not None: x, w = x[mask], w[mask]
    ok = ~np.isnan(x)
    x, w = x[ok], w[ok]
    W = w.sum(); m = (w*x).sum()/W
    var = (w**2*(x-m)**2).sum()/W**2
    return m, np.sqrt(var)

fine, coarse = [], []
for y in sorted(meta):
    cols = meta[y]["cols"]
    me = [f"MON_EXP_{i}" for i in range(1,6)]
    has_fine = all(c in cols for c in me)
    use = ["WT_DOM"] + [v for v in OFFV.values() if v in cols] + [v for v in CNT.values() if v in cols] + (me if has_fine else [])
    df,_ = pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"), usecols=list(dict.fromkeys(use)))
    w = df["WT_DOM"].values.astype(float)
    POS = 100.0 if y=="2025" else 1.0
    off = {k:(df[v].values==POS) for k,v in OFFV.items() if v in df.columns}

    r = {"year":int(y), "n":len(df)}
    for k in ("tour","etc","dom"):
        if k in off:
            p,s = wp(off[k], w); r[f"off_{k}"]=round(p,2); r[f"off_{k}_se"]=round(s,3)
    # coarse intensity: trips per participant
    for k in ("tour","etc"):
        if CNT[k] in df.columns and k in off:
            x = df[CNT[k]].values.astype(float)
            m,s = wmean(x, w)                       # per capita
            mi,si = wmean(x, w, mask=off[k])        # per participant
            r[f"cap_{k}"]=round(m,4); r[f"int_{k}"]=round(mi,4); r[f"int_{k}_se"]=round(si,4)
    coarse.append(r)

    if has_fine:
        E = {i:(df[f"MON_EXP_{i}"].values==1) for i in range(1,6)}
        f = {"year":int(y),"n":len(df)}
        for i in range(1,6):
            p,s = wp(E[i], w); f[f"p{i}"]=round(p,2); f[f"p{i}_se"]=round(s,3)
        p,s = wp(E[2]|E[3], w); f["vfr_any"]=round(p,2); f["vfr_any_se"]=round(s,3)
        # mapping verification
        if "tour" in off:
            u=E[1]|E[2]|E[4]; f["map_tour"]=round(np.mean(u==off["tour"])*100,3)
        if "etc" in off:
            u=E[3]|E[5];      f["map_etc"] =round(np.mean(u==off["etc"])*100,3)
        # hidden VFR: MON_EXP_2 as share of official tour participation
        if "tour" in off:
            f["hidden_share"]=round(f["p2"]/f["off_tour" if False else "p2"]*0,2)  # placeholder
        fine.append(f)
    print(y, "ok")

F = pd.DataFrame(fine); C = pd.DataFrame(coarse)
pd.set_option("display.width",250)
print("\n=== MAPPING VERIFICATION (official aggregates vs raw purpose) ===")
print(F[["year","n","map_tour","map_etc"]].to_string(index=False))
print("\n=== FINE PURPOSE PARTICIPATION, weighted %, SE ignores clustering ===")
print(F[["year","p1","p1_se","p2","p2_se","p3","p3_se","p4","p5","vfr_any","vfr_any_se"]].to_string(index=False))
print("\n=== COARSE, 8 waves: official participation % and trips ===")
print(C[["year","n","off_tour","off_etc","cap_tour","int_tour","cap_etc","int_etc"]].to_string(index=False))
F.to_csv(os.path.join(D,"final_fine.csv"),index=False); C.to_csv(os.path.join(D,"final_coarse.csv"),index=False)
print("\nsaved final_fine.csv, final_coarse.csv")
