import pandas as pd, numpy as np, pyarrow.parquet as pq, json, time
r=pq.read_table("core.parquet",columns=["ga","created","closed","resident","dup","completed","recur30","recur90"]).to_pandas()
foc=r[r.recur30.notna()].sample(3000,random_state=11)
res=r[r.resident & r.ga.isin(foc.ga.unique())][["ga","created"]].sort_values(["ga","created"])
grp={k:v.created.values for k,v in res.groupby("ga")}
bad30=bad90=0
for _,f in foc.iterrows():
    c=grp.get(f.ga,np.array([],dtype="datetime64[ns]")); after=c[c>f.closed]
    gap=(after.min()-np.datetime64(f.closed))/np.timedelta64(1,"D") if len(after) else np.inf
    # minute-resolution tie rule used in production: created strictly after closure minute
    b30=float(gap<=30); b90=float(gap<=90)
    bad30+= b30!=f.recur30
    if not np.isnan(f.recur90): bad90+= b90!=f.recur90
import json as _j; _o={"checked":len(foc),"mismatch30":int(bad30),"mismatch90":int(bad90),"rate30_sample":float(foc.recur30.mean())}; _j.dump(_o,open("tabs/recurrence_audit.json","w")); print(_o)
