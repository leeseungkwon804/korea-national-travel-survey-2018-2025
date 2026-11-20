import numpy as np, os
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
BLUE="#0072B2"; VERM="#D55E00"; GREY="#8C8C8C"; CM=1/2.54
yrs=[2020,2021,2022,2023,2024,2025]
pe=[0.364,-0.139,-0.369,-0.602,-0.381,-0.503]
sp=[0.314,-0.132,-0.473,-0.664,-0.331,-0.512]
fig,ax=plt.subplots(figsize=(12*CM,7.6*CM))
ax.axhline(0,color="black",lw=0.9)
ax.axvspan(2019.6,2020.5,color="#F2F2F2",zorder=0)
ax.plot(yrs,pe,marker="o",ms=4.2,lw=1.8,color=BLUE,label="Pearson",clip_on=False)
ax.plot(yrs,sp,marker="s",ms=4.0,lw=1.5,color=VERM,label="Spearman",clip_on=False,ls=(0,(5,2)))
ax.annotate("+0.364",(2020,0.364),xytext=(0,6),textcoords="offset points",ha="center",fontsize=7.5,color=BLUE)
ax.annotate("-0.503",(2025,-0.503),xytext=(6,-2),textcoords="offset points",fontsize=7.5,color=BLUE)
ax.set_xticks(yrs); ax.set_xlim(2019.6,2025.6); ax.set_ylim(-0.78,0.52)
ax.yaxis.set_major_locator(MultipleLocator(0.25))
ax.set_ylabel("Correlation between subsystem resilience indices")
ax.set_title("Sign reversal of the coupling between subsystems",pad=6)
ax.legend(loc="lower left",handlelength=1.7)
p=os.path.join(OB,"Figure5.png"); fig.savefig(p,bbox_inches="tight",pad_inches=0.02); plt.close(fig)
print("B Figure5", f"{os.path.getsize(p)/1024:.0f} KB")
