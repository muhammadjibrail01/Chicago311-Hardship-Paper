# Step 12: ward-by-month fixed effects (handles the mid-2023 ward-map switch) and the effect of pooling
# city-generated records. Paper: ward x month 0.023 (SE 0.008); resident-only 0.066 vs pooled 0.055.
import json, gc, numpy as np
from prep import get; from fe import feols
out={}
r=get(["lhrs"]); r["wm"]=(r.ward.astype(np.int64)*1000+r.ym.astype(np.int64))
m=feols(r,"lhrs",["hs","lwl"],fes=["ty","ym","dow","hod","chan","wm"])
out["ward_month"]={"b":float(m["coef"]["hs"]),"se":float(m["se"]["hs"]),"p":float(m["p"]["hs"]),"n":int(m["n"])}
s=r[r.year==2023]; pre=s[s.ym<12*4+4]; post=s[s.ym>=12*4+5]
tp=pre.groupby("ca").ward.agg(lambda x:x.value_counts().index[0]); tq=post.groupby("ca").ward.agg(lambda x:x.value_counts().index[0])
out["share_CAs_modal_ward_changed_in_2023"]=float((tp!=tq.reindex(tp.index)).mean()); del r,s,pre,post; gc.collect()
r=get(["lhrs","dup","completed","hrs","speed_s","resident"],filt=None); base=(~r.dup)&r.completed&(r.hrs>=0)
for nm,d in [("resident_only",r[base & r.resident]),("incl_city_generated",r[base])]:
    m=feols(d,"lhrs",["hs","lwl"],fes=["ty","ym","dow","hod"])   # no channel effects: mimics an analysis that pools all records
    out[nm]={"b":float(m["coef"]["hs"]),"se":float(m["se"]["hs"]),"n":int(m["n"])}
json.dump(out,open("tabs/extra_robustness.json","w"),indent=1); print(json.dumps(out))
