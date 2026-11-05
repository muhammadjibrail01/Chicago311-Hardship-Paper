# Step 16: raw 311 data audit: row counts, unique request IDs, timestamp parse failures, status/duplicate/legacy values.
import glob, json, numpy as np, pandas as pd, pyarrow.parquet as pq
tot=0; natc=0; natcl=0; bad=0; h=[]; st={}; du={}; lg={}
for f in sorted(glob.glob("data311/p_*.parquet")):
    t=pq.read_table(f,columns=["SR_NUMBER","CREATED_DATE","CLOSED_DATE","STATUS","DUPLICATE","LEGACY_RECORD"]).to_pandas()
    tot+=len(t); natc+=int(t.CREATED_DATE.isna().sum()); natcl+=int(t.CLOSED_DATE.isna().sum()); bad+=int((t.CLOSED_DATE<t.CREATED_DATE).sum())
    h.append(pd.util.hash_pandas_object(t.SR_NUMBER,index=False).values)
    for d,c in [(st,"STATUS"),(du,"DUPLICATE"),(lg,"LEGACY_RECORD")]:
        for k,v in t[c].value_counts(dropna=False).items(): d[str(k)]=d.get(str(k),0)+int(v)
    del t
out={"rows":tot,"unique_ids":int(len(np.unique(np.concatenate(h)))),"created_parse_failures":natc,"closed_missing":natcl,"closed_before_created":bad,"status":st,"duplicate":du,"legacy":lg}
json.dump(out,open("tabs/raw_audit.json","w"),indent=1); print(json.dumps(out))
