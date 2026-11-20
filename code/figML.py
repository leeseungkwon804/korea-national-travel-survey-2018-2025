import pandas as pd, numpy as np, os, json, pyreadstat
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


import os
# Paths are read from the environment so the code is portable.
#   NTS_DATA : directory holding the extracted SPSS files (YYYY_domestic.sav)
#   NTS_OUT  : directory for tables and figures
D   = os.environ.get("NTS_DATA", "./data")
OUT = os.environ.get("NTS_OUT",  "./outputs")
OA  = os.path.join(OUT, "paperA_figs")
OB  = os.path.join(OUT, "paperB_figs")
os.makedirs(OA, exist_ok=True); os.makedirs(OB, exist_ok=True)

plt.rcParams.update({"font.family":"Arial","font.size":8,"axes.labelsize":8,"axes.titlesize":9,
 "xtick.labelsize":7.5,"ytick.labelsize":7.5,"legend.fontsize":7.3,"axes.linewidth":0.6,
 "xtick.major.width":0.6,"ytick.major.width":0.6,"axes.spines.top":False,"axes.spines.right":False,
 "savefig.dpi":600,"figure.dpi":600,"legend.frameon":False,"axes.grid":True,
 "grid.color":"#E6E6E6","grid.linewidth":0.5,"axes.axisbelow":True})
BLUE="#0072B2"; VERM="#D55E00"; GREY="#8C8C8C"; GREEN="#009E73"; CM=1/2.54

# ---- Paper A Figure 5 : permutation importance 2019 vs 2025 ----
a=pd.read_csv(os.path.join(D,"ml_importance_2019.csv")).set_index("feature")
b=pd.read_csv(os.path.join(D,"ml_importance_2025.csv")).set_index("feature")
order=b.sort_values("drop_in_AUC",ascending=True).index.tolist()
y=np.arange(len(order)); h=0.38
fig,ax=plt.subplots(figsize=(12*CM,9*CM))
ax.barh(y-h/2,[a.loc[f,"drop_in_AUC"] for f in order],h,color=GREY,label="2019",
        xerr=[a.loc[f,"sd"] for f in order],error_kw=dict(elinewidth=0.7,ecolor="#555"))
ax.barh(y+h/2,[b.loc[f,"drop_in_AUC"] for f in order],h,color=BLUE,label="2025",
        xerr=[b.loc[f,"sd"] for f in order],error_kw=dict(elinewidth=0.7,ecolor="#555"))
ax.set_yticks(y); ax.set_yticklabels(order)
ax.set_xlabel("Mean drop in AUC when the feature is permuted")
ax.set_title("What distinguishes substitution from withdrawal",pad=6)
ax.legend(loc="lower right",handlelength=1.4); ax.set_xlim(-0.004,0.08)
p=os.path.join(OA,"Figure5.png"); fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
print("A Figure5", f"{os.path.getsize(p)/1024:.0f} KB")

# ---- Paper A Figure 6 : model comparison ----
fig,ax=plt.subplots(figsize=(10*CM,6.6*CM))
models=["Income only","All features\nlogistic","Gradient\nboosting"]
v19=[0.5221,0.6216,0.6598]; v25=[0.5579,0.6325,0.6532]
x=np.arange(3); w=0.36
ax.bar(x-w/2,v19,w,color=GREY,label="2019",edgecolor="white",lw=0.8)
ax.bar(x+w/2,v25,w,color=BLUE,label="2025",edgecolor="white",lw=0.8)
ax.axhline(0.5,color=VERM,lw=1.1,ls=(0,(4,3)))
for i,(u,v) in enumerate(zip(v19,v25)):
    ax.annotate(f"{u:.3f}",(i-w/2,u),xytext=(0,3),textcoords="offset points",ha="center",fontsize=6.8)
    ax.annotate(f"{v:.3f}",(i+w/2,v),xytext=(0,3),textcoords="offset points",ha="center",fontsize=6.8)
ax.set_xticks(x); ax.set_xticklabels(models)
ax.set_ylabel("Held out AUC"); ax.set_ylim(0.45,0.72)
ax.yaxis.set_major_locator(MultipleLocator(0.05))
ax.set_title("Predictive performance against simple baselines",pad=6)
ax.legend(loc="upper left",handlelength=1.4)
p=os.path.join(OA,"Figure6.png"); fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
print("A Figure6", f"{os.path.getsize(p)/1024:.0f} KB")

# ---- Paper B Figure 3 : subsystem time paths, capital region vs rest ----
R=pd.read_csv(os.path.join(D,"regional_panel.csv"))
CAP=["Seoul","Gyeonggi","Incheon"]
g=R.assign(grp=np.where(R.region.isin(CAP),"Capital region","Other regions")) \
   .groupby(["grp","year"],as_index=False)[["night","day"]].mean()
fig,axes=plt.subplots(1,2,figsize=(16*CM,7*CM))
for ax,col,ttl in zip(axes,["night","day"],["Overnight subsystem","Day trip subsystem"]):
    for grp,c,mk in (("Capital region",VERM,"o"),("Other regions",BLUE,"s")):
        s=g[g.grp==grp]
        base=s[s.year==2019][col].iloc[0]
        ax.plot(s.year,s[col]/base*100,marker=mk,ms=3.8,lw=1.7,color=c,label=grp,clip_on=False)
    ax.axhline(100,color=GREY,lw=0.8,ls=(0,(4,3)))
    ax.set_xticks(sorted(g.year.unique())); ax.set_xticklabels([str(v) for v in sorted(g.year.unique())],rotation=45,ha="right")
    ax.set_ylabel("Participation, 2019 equals 100"); ax.set_title(ttl,pad=5)
    ax.set_ylim(35,175); ax.yaxis.set_major_locator(MultipleLocator(25))
axes[0].legend(loc="lower right",handlelength=1.5)
fig.suptitle("Divergent subsystem trajectories, capital region and the rest",y=1.03,fontsize=9)
p=os.path.join(OB,"Figure3.png"); fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
print("B Figure3", f"{os.path.getsize(p)/1024:.0f} KB")

# ---- Paper B Figure 4 : ranked day-subsystem resilience ----
S=pd.read_csv(os.path.join(D,"regional_std.csv")).sort_values("day_idx_std")
fig,ax=plt.subplots(figsize=(12*CM,9*CM))
y=np.arange(len(S))
ax.barh(y,S.day_idx_std,0.62,color=[VERM if v<100 else GREEN for v in S.day_idx_std],edgecolor="white",lw=0.7)
ax.axvline(100,color=GREY,lw=1.0,ls=(0,(4,3)))
ax.set_yticks(y); ax.set_yticklabels(S.region); ax.invert_yaxis()
ax.set_xlabel("Day trip participation, age standardised, 2019 equals 100")
ax.set_xlim(0,175); ax.xaxis.set_major_locator(MultipleLocator(25))
ax.set_title("Regional resilience of the day trip subsystem",pad=6)
p=os.path.join(OB,"Figure4.png"); fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
print("B Figure4", f"{os.path.getsize(p)/1024:.0f} KB")
