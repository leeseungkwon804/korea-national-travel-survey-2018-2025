import pyreadstat, glob, os, json

import os
# Paths are read from the environment so the code is portable.
#   NTS_DATA : directory holding the extracted SPSS files (YYYY_domestic.sav)
#   NTS_OUT  : directory for tables and figures
D   = os.environ.get("NTS_DATA", "./data")
OUT = os.environ.get("NTS_OUT",  "./outputs")
OA  = os.path.join(OUT, "paperA_figs")
OB  = os.path.join(OUT, "paperB_figs")
os.makedirs(OA, exist_ok=True); os.makedirs(OB, exist_ok=True)

rows = {}
for f in sorted(glob.glob(os.path.join(D, "*_domestic.sav"))):
    y = os.path.basename(f)[:4]
    try:
        df, m = pyreadstat.read_sav(f, metadataonly=True)
        rows[y] = {"n": m.number_rows, "k": m.number_columns, "cols": list(m.column_names)}
        print(f"{y}: rows={m.number_rows:,}  cols={m.number_columns:,}  enc={m.file_encoding}")
    except Exception as e:
        print(f"{y}: ERROR {type(e).__name__} {e}")
json.dump(rows, open(os.path.join(D, "_meta_domestic.json"), "w"), ensure_ascii=False)
print()
# which key vars exist in every year?
KEY = ["BSEX","BAGE","BARA","BEDU","BMAR","BFAM","BINC1","BINC2","BJOB","BMON","WT_DOM","ID"]
years = sorted(rows)
print("var        " + "  ".join(years))
for k in KEY:
    print(f"{k:<10} " + "  ".join(("O   " if k in rows[y]["cols"] else ".   ") for y in years))
