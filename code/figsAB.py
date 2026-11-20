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
BLUE="#0072B2"; VERM="#D55E00"; GREEN="#009E73"; PURP="#CC79A7"; GREY="#8C8C8C"
CM=1/2.54
def save(fig,p):
    fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
    print("wrote",os.path.basename(p),f"{os.path.getsize(p)/1024:.0f} KB")

# ---------- PAPER A : income bands, 8 waves ----------
meta=json.load(open(os.path.join(D,"_meta_domestic.json")))
INC={1:"<1.0",2:"1.0-2.0",3:"2.0-3.0",4:"3.0-4.0",5:"4.0-5.0",6:"5.0-6.0",7:"6.0+"}
rows=[]
for y in sorted(meta):
    use=[c for c in ["국내_월별여행경험_관광숙박","국내_월별여행경험_관광당일","BINC1","WT_DOM"] if c in meta[y]["cols"]]
    d,_=pyreadstat.read_sav(os.path.join(D,f"{y}_domestic.sav"),usecols=use)
    w=d["WT_DOM"].values.astype(float); POS=100.0 if y=="2025" else 1.0
    nt=(d["국내_월별여행경험_관광숙박"].values==POS); dy=(d["국내_월별여행경험_관광당일"].values==POS)
    for k,lab in INC.items():
        sel=(d["BINC1"].values==k)
        if w[sel].sum()<=0 or sel.sum()<200: continue
        rows.append(dict(year=int(y),band=lab,k=k,
            night=w[sel&nt].sum()/w[sel].sum()*100, day=w[sel&dy].sum()/w[sel].sum()*100))
A=pd.DataFrame(rows); A.to_csv(os.path.join(D,"income_panel.csv"),index=False)
b19=A[A.year==2019].set_index("k")

# A-Fig1 : overnight participation by income band, 2019 vs 2025
fig,ax=plt.subplots(figsize=(12.5*CM,7.4*CM))
x=np.arange(7); wdt=0.38
a19=[b19.loc[k,"night"] for k in range(1,8)]
a25=[A[(A.year==2025)&(A.k==k)]["night"].iloc[0] for k in range(1,8)]
ax.bar(x-wdt/2,a19,wdt,color=GREY,label="2019",edgecolor="white",lw=0.8)
ax.bar(x+wdt/2,a25,wdt,color=BLUE,label="2025",edgecolor="white",lw=0.8)
for i,(u,v) in enumerate(zip(a19,a25)):
    ax.annotate(f"{(v/u-1)*100:+.0f}%",(i,max(u,v)),xytext=(0,3),textcoords="offset points",
                ha="center",fontsize=7,color=VERM)
ax.set_xticks(x); ax.set_xticklabels(list(INC.values()),rotation=30,ha="right")
ax.set_xlabel("Monthly household income, million KRW"); ax.set_ylabel("Participation, percent")
ax.set_ylim(0,33); ax.yaxis.set_major_locator(MultipleLocator(10))
ax.set_title("Overnight leisure travel participation by household income",pad=6)
ax.legend(loc="upper left",handlelength=1.4)
save(fig,os.path.join(OA,"Figure1.png"))

# A-Fig2 : indexed trajectories, low vs high band, both trip types
fig,axes=plt.subplots(1,2,figsize=(16*CM,7*CM))
yrs=sorted(A.year.unique())
def idx(k,col):
    base=b19.loc[k,col]; return [A[(A.year==y)&(A.k==k)][col].iloc[0]/base*100 for y in yrs]
for ax,col,ttl in zip(axes,["night","day"],["Overnight trips","Day trips"]):
    ax.axhline(100,color=GREY,lw=0.8,ls=(0,(4,3)))
    ax.plot(yrs,idx(1,col),marker="o",ms=3.8,lw=1.7,color=VERM,label="Lowest band",clip_on=False)
    ax.plot(yrs,idx(4,col),marker="s",ms=3.8,lw=1.7,color=GREEN,label="Middle band",clip_on=False)
    ax.plot(yrs,idx(7,col),marker="^",ms=3.8,lw=1.7,color=BLUE,label="Highest band",clip_on=False)
    ax.set_xticks(yrs); ax.set_xticklabels([str(v) for v in yrs],rotation=45,ha="right")
    ax.set_ylabel("Participation, 2019 equals 100"); ax.set_title(ttl,pad=5)
    ax.set_ylim(20,180); ax.yaxis.set_major_locator(MultipleLocator(40))
axes[0].legend(loc="lower right",handlelength=1.5)
fig.suptitle("Trajectories by household income band",y=1.03,fontsize=9)
save(fig,os.path.join(OA,"Figure2.png"))

# A-Fig3 : substitution vs exit scatter
fig,ax=plt.subplots(figsize=(10.5*CM,8*CM))
dn=[A[(A.year==2025)&(A.k==k)]["night"].iloc[0]-b19.loc[k,"night"] for k in range(1,8)]
dd=[A[(A.year==2025)&(A.k==k)]["day"].iloc[0]-b19.loc[k,"day"] for k in range(1,8)]
sc=ax.scatter(dn,dd,s=58,c=range(7),cmap="viridis",edgecolor="white",linewidth=0.9,zorder=3)
for i,lab in enumerate(INC.values()):
    ax.annotate(lab,(dn[i],dd[i]),xytext=(6,-2),textcoords="offset points",fontsize=7)
ax.axhline(0,color=GREY,lw=0.8); ax.axvline(0,color=GREY,lw=0.8)
ax.set_xlabel("Change in overnight participation, percentage points")
ax.set_ylabel("Change in day-trip participation, percentage points")
ax.set_title("Substitution and withdrawal by income band",pad=6)
save(fig,os.path.join(OA,"Figure3.png"))

# ---------- PAPER B : regional ----------
R=pd.read_csv(os.path.join(D,"regional_resilience.csv"),index_col=0)
R=R.sort_values("night_idx")
fig,ax=plt.subplots(figsize=(12*CM,9*CM))
y=np.arange(len(R))
ax.barh(y,R.night_idx,0.62,color=[VERM if v<100 else BLUE for v in R.night_idx],edgecolor="white",lw=0.7)
ax.axvline(100,color=GREY,lw=1.0,ls=(0,(4,3)))
ax.set_yticks(y); ax.set_yticklabels(R.index); ax.invert_yaxis()
ax.set_xlabel("Overnight participation, 2019 equals 100"); ax.set_xlim(0,145)
ax.xaxis.set_major_locator(MultipleLocator(25))
ax.set_title("Regional resilience of the overnight subsystem",pad=6)
save(fig,os.path.join(OB,"Figure1.png"))

fig,ax=plt.subplots(figsize=(10.5*CM,8.4*CM))
ax.scatter(R.night_idx,R.day_idx,s=52,color=BLUE,edgecolor="white",linewidth=0.9,zorder=3)
for nm,r in R.iterrows():
    ax.annotate(nm,(r.night_idx,r.day_idx),xytext=(5,-2),textcoords="offset points",fontsize=6.8)
z=np.polyfit(R.night_idx,R.day_idx,1); xs=np.linspace(R.night_idx.min(),R.night_idx.max(),10)
ax.plot(xs,np.polyval(z,xs),color=VERM,lw=1.5,zorder=2)
ax.axhline(100,color=GREY,lw=0.7); ax.axvline(100,color=GREY,lw=0.7)
ax.set_xlabel("Overnight subsystem, 2019 equals 100")
ax.set_ylabel("Day-trip subsystem, 2019 equals 100")
ax.set_title("Negative coupling between the two subsystems",pad=6)
save(fig,os.path.join(OB,"Figure2.png"))
print("\ncorr =", round(R.night_idx.corr(R.day_idx),3))
