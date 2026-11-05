import json, gc, numpy as np, pandas as pd, pyarrow.parquet as pq
from prep import get; from fe import feols, demean
OUT={}
# ---- C1/C2 on the baseline speed sample
r=get(["lhrs"]); ca=pd.read_csv("ca.csv").set_index("ca")
wy=pd.factorize(r.wy)[0]; hs=r.hs.values.astype(float)
gm=np.bincount(wy,weights=hs)/np.bincount(wy); OUT["within_ward_share_hs_var"]=float(np.var(hs-gm[wy])/np.var(hs))
M=demean(r[["lhrs","hs","lwl"]].to_numpy(float),[r[f].to_numpy() for f in ["ty","ym","dow","hod","chan"]])
y,x,l=M[:,0],M[:,1],M[:,2]; x=x-l*(x@l)/(l@l); y=y-l*(y@l)/(l@l)
beta=(x@y)/(x@x); g=pd.factorize(r.ca.values)[0]; cav=pd.factorize(r.ca.values)[1]
Sxy=np.bincount(g,weights=x*y); Sxx=np.bincount(g,weights=x*x)
loo=(Sxy.sum()-Sxy)/(Sxx.sum()-Sxx)
OUT["beta_fwl"]=float(beta); OUT["loo_min"]=float(loo.min()); OUT["loo_max"]=float(loo.max())
OUT["loo_min_ca"]=ca.loc[int(cav[loo.argmin()]),"name"]; OUT["loo_max_ca"]=ca.loc[int(cav[loo.argmax()]),"name"]
top=np.argsort(-np.abs(loo-beta))[:3]; OUT["most_influential"]={ca.loc[int(cav[i]),"name"]:round(float(loo[i]),4) for i in top}
# drop the 5 most influential jointly
o=np.argsort(-np.abs(Sxy/Sxx.sum()))[:5]; keep=~np.isin(g,o); OUT["drop5_influential"]=float((x[keep]@y[keep])/(x[keep]@x[keep]))
del M,x,y,l; gc.collect()
# ---- C6: decomposition total, recomputed directly
q=r[r.hq.isin([1,4])]; OUT["raw_gap_q4_q1"]=float(q[q.hq==4].lhrs.mean()-q[q.hq==1].lhrs.mean())
del r,q; gc.collect()
# ---- ambiguous origins reclassified as resident (phone)
core=pd.read_csv("tabs/core_types.csv").iloc[:,0].tolist()
o=pq.read_table("req.parquet",columns=["type","origin"],read_dictionary=["type","origin"]).to_pandas()
o=o[o.type.isin(core)].origin.astype(str).values
r=get(["lhrs","dup","completed","hrs","speed_s"],filt=None)
assert len(r)==len(o); amb=np.isin(o,["Salesforce Mobile App","SPOTCSR","CSCC"]); del o
OUT["ambiguous_n"]=int(amb.sum())
add=amb & ~r.dup.values & r.completed.values & (r.hrs.values>=0)
r["chan"]=r.chan.astype(str); r.loc[amb,"chan"]="phone"; r["chan"]=r.chan.astype("category")
s=r[r.speed_s.values | add]; OUT["ambiguous_added_to_speed"]=int(add.sum())
m=feols(s,"lhrs",["hs","lwl"],fes=["ty","ym","dow","hod","chan"])
OUT["amb_as_resident"]={"b":float(m["coef"]["hs"]),"se":float(m["se"]["hs"]),"n":int(m["n"])}
json.dump(OUT,open("tabs/audit_models.json","w"),default=float,indent=1); print(json.dumps(OUT,default=float))
