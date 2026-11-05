import pandas as pd, numpy as np, pyarrow.parquet as pq
def get(cols, filt="speed_s"):
    base=["type","chan","year","ym","dow","hod","ca","ward","hardship","hq","lwl"]
    c=list(dict.fromkeys(base+cols+([filt] if filt else [])))
    r=pq.read_table("core.parquet",columns=c,read_dictionary=["type","chan"]).to_pandas()
    if filt: r=r[r[filt]==True].copy()
    ca=pd.read_csv("ca.csv").set_index("ca")
    mu,sd=ca.hardship.mean(),ca.hardship.std()
    r["hs"]=((r.hardship-mu)/sd).astype("float32")
    for v in ["density","dist_loop_km","viol_rate","lowinc","pct_black","pct_hisp","pct_asian","pct_65","bviol_rate","pop"]:
        r[v]=r.ca.map(ca[v]).astype("float32")
    r["ldens"]=np.log(r.density); r["lpop"]=np.log(r["pop"])
    r["type"]=r.type.astype(str).astype("category")
    r["ty"]=(r.type.cat.codes.astype(np.int32)*10+(r.year-2019)).astype(np.int32)
    r["wy"]=(r.ward.astype(np.int32)*10+(r.year-2019)).astype(np.int32)
    r["tyc"]=(r.ty.astype(np.int64)*10+r.chan.cat.codes).astype(np.int64)
    return r
