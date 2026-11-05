# Step 0: if the 311 data are only available as a .7z archive, extract the CSVs into WORK_DIR/311_csv.
import os, glob, sys
from config import RAW_DIR, WORK_DIR, raw_files
if raw_files("311_Service_Requests*.csv"):
    print("311 CSV files found; nothing to extract."); sys.exit(0)
arcs = glob.glob(os.path.join(RAW_DIR, "*311*Service*Requests*.7z"))
if not arcs: raise FileNotFoundError("No 311 CSV files or .7z archive found in RAW_DIR.")
import py7zr
out = os.path.join(WORK_DIR, "311_csv"); os.makedirs(out, exist_ok=True)
for a in arcs:
    with py7zr.SevenZipFile(a) as z: z.extractall(out)
    print("extracted", os.path.basename(a))
