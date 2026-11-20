import zipfile, io, os, re, sys

import os
# Paths are read from the environment so the code is portable.
#   NTS_DATA : directory holding the extracted SPSS files (YYYY_domestic.sav)
#   NTS_OUT  : directory for tables and figures
D   = os.environ.get("NTS_DATA", "./data")
OUT = os.environ.get("NTS_OUT",  "./outputs")
OA  = os.path.join(OUT, "paperA_figs")
OB  = os.path.join(OUT, "paperB_figs")
os.makedirs(OA, exist_ok=True); os.makedirs(OB, exist_ok=True)

DEST = D
os.makedirs(DEST, exist_ok=True)

def kname(info):
    if info.flag_bits & 0x800:
        return info.orig_filename
    raw = info.orig_filename.encode("cp437", errors="replace")
    for enc in ("cp949","utf-8"):
        try: return raw.decode(enc)
        except Exception: pass
    return info.orig_filename

OUT = {
 OUT: ["2018","2019","2020","2021"],
 OUT: ["2022","2023","2024"],
 OUT: ["2025"],
}

# inner-member classification: domestic vs overseas, by Korean token OR mojibake fallback on member order
DOM_TOK = ("국내",)
OVS_TOK = ("해외",)

written = []
for p, years in OUT.items():
    with zipfile.ZipFile(p) as z:
        for info in z.infolist():
            outer = kname(info)
            m = re.search(r"(20\d\d)", outer)
            if not m or m.group(1) not in years:
                continue
            year = m.group(1)
            outer_is_dom = any(t in outer for t in DOM_TOK)
            outer_is_ovs = any(t in outer for t in OVS_TOK)
            blob = z.read(info)
            with zipfile.ZipFile(io.BytesIO(blob)) as iz:
                for ii in iz.infolist():
                    inm = kname(ii)
                    if not inm.lower().endswith(".sav"):
                        continue
                    if "국내" in inm: kind = "domestic"
                    elif "해외" in inm: kind = "overseas"
                    elif outer_is_dom: kind = "domestic"
                    elif outer_is_ovs: kind = "overseas"
                    else: kind = "unknown"
                    tag = f"{year}_{kind}"
                    # disambiguate if duplicate
                    base = os.path.join(DEST, tag + ".sav")
                    n = 1
                    while os.path.exists(base):
                        base = os.path.join(DEST, f"{tag}_{n}.sav"); n += 1
                    with iz.open(ii) as src, open(base, "wb") as dst:
                        while True:
                            chunk = src.read(1 << 22)
                            if not chunk: break
                            dst.write(chunk)
                    written.append((os.path.basename(base), ii.file_size, inm))
                    print(f"  OK {os.path.basename(base):<24} {ii.file_size:>13,}  <- {inm}")
            del blob

print()
print(f"{len(written)} .sav files written to {DEST}")
