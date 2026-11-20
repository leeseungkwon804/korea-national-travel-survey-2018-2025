import pyreadstat, os, json, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline

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
FEAT=["BINC1","BAGE","BSEX","BEDU","BMAR","BFAM","BJOB","BARA","BMON","DQ7","DQ2A","DQ5"]
NICE={"BINC1":"Household income","BAGE":"Age group","BSEX":"Sex","BEDU":"Education",
      "BMAR":"Marital status","BFAM":"Household size","BJOB":"Occupation","BARA":"Region",
      "BMON":"Survey month","DQ7":"Car ownership","DQ2A":"Children in household","DQ5":"In employment"}

def prep(y):
    use=[c for c in FEAT+["국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","WT_DOM"] if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use)
    if y=="2019" and "BARA" in d:
        d["BARA"]=[MAP.get(int(x),np.nan) if not np.isnan(x) else np.nan for x in d["BARA"].values]
    POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS)
    dy=(d["국내_월별여행경험_관광당일"].values==POS)
    sub=d.loc[~nt].copy()                       # no overnight trip
    yv=dy[~nt].astype(int)                      # took a day trip anyway = substitution
    cols=[c for c in FEAT if c in sub.columns]
    X=sub[cols].astype(float)
    X=X.replace({99.0:np.nan})
    w=sub["WT_DOM"].values.astype(float)
    return X,yv,w,cols

for Y in ("2019","2025"):
    X,yv,w,cols=prep(Y)
    print(f"\n######## {Y}  n={len(X):,}  substitution rate={yv.mean()*100:.2f}%  features={len(cols)}")
    Xtr,Xte,ytr,yte,wtr,wte=train_test_split(X,yv,w,test_size=0.30,random_state=11,stratify=yv)
    # baselines
    base_rate=ytr.mean()
    auc_const=0.5
    inc=Xtr[["BINC1"]].fillna(-1); incte=Xte[["BINC1"]].fillna(-1)
    lr_inc=LogisticRegression(max_iter=400).fit(inc,ytr,sample_weight=wtr)
    p_inc=lr_inc.predict_proba(incte)[:,1]
    Xtr_f=Xtr.fillna(-1); Xte_f=Xte.fillna(-1)
    lr_all=LogisticRegression(max_iter=800).fit(Xtr_f,ytr,sample_weight=wtr)
    p_lr=lr_all.predict_proba(Xte_f)[:,1]
    gb=HistGradientBoostingClassifier(max_iter=250,learning_rate=0.06,max_depth=6,
        l2_regularization=1.0,random_state=11)
    gb.fit(Xtr,ytr,sample_weight=wtr)
    p_gb=gb.predict_proba(Xte)[:,1]
    print(f"  base rate (test)            = {yte.mean()*100:5.2f}%")
    print(f"  AUC  income only (logit)    = {roc_auc_score(yte,p_inc,sample_weight=wte):.4f}")
    print(f"  AUC  all features (logit)   = {roc_auc_score(yte,p_lr ,sample_weight=wte):.4f}")
    print(f"  AUC  gradient boosting      = {roc_auc_score(yte,p_gb ,sample_weight=wte):.4f}")
    print(f"  PR-AUC gradient boosting    = {average_precision_score(yte,p_gb,sample_weight=wte):.4f}")
    r=permutation_importance(gb,Xte,yte,n_repeats=6,random_state=11,
                             scoring="roc_auc",sample_weight=wte,n_jobs=1)
    imp=pd.DataFrame({"feature":[NICE.get(c,c) for c in cols],
                      "drop_in_AUC":r.importances_mean,"sd":r.importances_std}).sort_values("drop_in_AUC",ascending=False)
    print("  permutation importance (mean drop in AUC):")
    for _,row in imp.iterrows():
        print(f"     {row.feature:<24} {row.drop_in_AUC:+.4f}  (sd {row.sd:.4f})")
    imp.to_csv(os.path.join(D,f"ml_importance_{Y}.csv"),index=False)
