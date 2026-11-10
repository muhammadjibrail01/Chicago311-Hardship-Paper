import pandas as pd, numpy as np, json, warnings; warnings.filterwarnings("ignore")
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test
from prep import get
r=get(["dup","completed","unresolved","hrs","created"],filt="resident"); r=r[~r.dup]
ext=pd.Timestamp("2026-09-23"); dur=np.where(r.unresolved,(ext-r.created).dt.total_seconds()/3600,r.hrs)
r["dur"]=np.maximum(dur,1e-3)/24; r["ev"]=r.completed.astype(int); r=r[np.isfinite(r.dur)]
s=r.sample(30000,random_state=5).copy()
for c in ["digital","alderman"]: s["c_"+c]=(s.chan==c).astype(float)
s["type"]=s.type.astype(str); X=["hs","c_digital","c_alderman","lwl"]
cph=CoxPHFitter().fit(s[["dur","ev","type"]+X],"dur","ev",strata=["type"])
t=proportional_hazard_test(cph,s[["dur","ev","type"]+X],time_transform="rank")
out={"hr_hs":float(np.exp(cph.params_["hs"])),"ph_test":{k:{"stat":float(t.summary.loc[k,"test_statistic"]),"p":float(t.summary.loc[k,"p"])} for k in X}}
json.dump(out,open("tabs/ph_test.json","w")); print(json.dumps(out))
