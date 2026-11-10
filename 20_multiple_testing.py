# Step 20: Benjamini-Hochberg and Bonferroni corrections for the 49 type-specific gradients (paper: 25/5 and 16/2 survive).
import json, numpy as np, pandas as pd
from scipy import stats
h=json.load(open("tabs/reg_het.json"))
f=pd.DataFrame([{"type":k.split("|",1)[1],"b":v["coef"],"se":v["se"]} for k,v in h.items() if k.startswith("type|")])
p=2*stats.t.sf(np.abs(f.b/f.se),76); m=len(p); o=np.argsort(p)
q=np.empty(m); q[o]=np.minimum.accumulate((p[o]*m/np.arange(1,m+1))[::-1])[::-1]; f["p"]=p; f["q_bh"]=np.minimum(q,1)
f["pct_per_sd"]=100*(np.exp(f.b)-1); f.to_csv("tabs/type_bh.csv",index=False)
out={"n_types":m,"raw_pos":int(((p<.05)&(f.b>0)).sum()),"raw_neg":int(((p<.05)&(f.b<0)).sum()),"bh_pos":int(((f.q_bh<.05)&(f.b>0)).sum()),
     "bh_neg":int(((f.q_bh<.05)&(f.b<0)).sum()),"bonf_pos":int(((p<.05/m)&(f.b>0)).sum()),"bonf_neg":int(((p<.05/m)&(f.b<0)).sum())}
json.dump(out,open("tabs/multiple_testing.json","w"),indent=1); print(out)
