# Step 2: request-level file. Excludes information-only calls and aircraft-noise complaints, keeps valid
# community areas (1-77) and the 2019-2024 window. Paper: 11,111,549 raw -> 5,210,130 analysis records.
import glob, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from config import START, END
cols=["SR_TYPE","OWNER_DEPARTMENT","STATUS","ORIGIN","CREATED_DATE","CLOSED_DATE","DUPLICATE","PARENT_SR_NUMBER","COMMUNITY_AREA","WARD","STREET_ADDRESS","LATITUDE","LONGITUDE"]
EXCL={"311 INFORMATION ONLY CALL","Aircraft Noise Complaint"}
lo, hi = pd.Timestamp(START), pd.Timestamp(END) + pd.Timedelta(days=1)
w=None; tot=[0,0,0,0]
for f in sorted(glob.glob("data311/p_*.parquet")):
    for b in pq.ParquetFile(f).iter_batches(batch_size=400_000, columns=cols):
        d=b.to_pandas(); tot[0]+=len(d)
        d=d[(d.CREATED_DATE>=lo)&(d.CREATED_DATE<hi)]; tot[1]+=len(d)
        d=d[~d.SR_TYPE.isin(EXCL)]; tot[2]+=len(d)
        d=d[d.COMMUNITY_AREA.between(1,77)]; tot[3]+=len(d)
        out=pd.DataFrame({"type":d.SR_TYPE.values,"dept":d.OWNER_DEPARTMENT.values,"status":d.STATUS.values,"origin":d.ORIGIN.values,
          "created":d.CREATED_DATE.values,"closed":d.CLOSED_DATE.values,"dup":(d.DUPLICATE=="true").values,"has_parent":d.PARENT_SR_NUMBER.notna().values,
          "ca":d.COMMUNITY_AREA.astype("int8").values,"ward":d.WARD.fillna(0).astype("int8").values,
          "addr":pd.util.hash_pandas_object(d.STREET_ADDRESS.fillna("").str.upper().str.strip(), index=False).values,
          "lat":d.LATITUDE.astype("float32").values,"lon":d.LONGITUDE.astype("float32").values})
        t=pa.Table.from_pandas(out, preserve_index=False)
        if w is None: w=pq.ParquetWriter("req.parquet", t.schema, compression="zstd")
        w.write_table(t.cast(w.schema)); del d,out,t
w.close(); print("raw, in 2019-2024 window, after excluded types, after valid community area:", [f"{x:,}" for x in tot])
