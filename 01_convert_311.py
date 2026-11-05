# Step 1: convert each 311 CSV to a compact Parquet file, streaming in chunks (works with ~3 GB of RAM).
# Files are named by their first calendar year so that later steps read them in chronological order,
# which keeps row order (and therefore every seeded random sample) identical to the paper.
import os, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from config import WORK_DIR, raw_files
cols = ["SR_NUMBER","SR_TYPE","SR_SHORT_CODE","OWNER_DEPARTMENT","STATUS","ORIGIN","CREATED_DATE","CLOSED_DATE",
        "DUPLICATE","LEGACY_RECORD","PARENT_SR_NUMBER","COMMUNITY_AREA","WARD","STREET_ADDRESS","LATITUDE","LONGITUDE"]
os.makedirs("data311", exist_ok=True)
files = raw_files("311_Service_Requests*.csv")
if not files: raise FileNotFoundError("No 311_Service_Requests*.csv found (run step 00 or see README).")
for i, f in enumerate(files):
    tmp = f"data311/tmp_{i}.parquet"; w = None; n = 0; ymin = 9999
    for ch in pd.read_csv(f, usecols=cols, dtype=str, chunksize=500_000):
        for c in ["CREATED_DATE","CLOSED_DATE"]:
            ch[c] = pd.to_datetime(ch[c], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
        for c in ["COMMUNITY_AREA","WARD","LATITUDE","LONGITUDE"]:
            ch[c] = pd.to_numeric(ch[c], errors="coerce")
        for c in ["SR_TYPE","SR_SHORT_CODE","OWNER_DEPARTMENT","STATUS","ORIGIN","DUPLICATE","LEGACY_RECORD"]:
            ch[c] = ch[c].astype("category").astype(str)
        ymin = min(ymin, int(ch.CREATED_DATE.dt.year.min()))
        t = pa.Table.from_pandas(ch, preserve_index=False)
        if w is None: w = pq.ParquetWriter(tmp, t.schema, compression="zstd")
        w.write_table(t.cast(w.schema)); n += len(ch)
    w.close(); os.replace(tmp, f"data311/p_{ymin}_{i}.parquet")
    print(f"{os.path.basename(f)}: {n:,} rows, first year {ymin}")
