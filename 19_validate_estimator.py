# Step 19 (optional): check the custom fixed-effects estimator (fe.py) against pyfixest on a 300,000-request subsample.
import json, sys
try: import pyfixest as pf
except ImportError: print("pyfixest not installed; skipping (optional step)."); sys.exit(0)
from prep import get; from fe import feols
r=get(["lhrs"]).sample(300_000,random_state=1)
a=feols(r,"lhrs",["hs","lwl"],fes=["ty","ym","chan"])
b=pf.feols("lhrs ~ hs + lwl | ty + ym + chan", data=r, vcov={"CRV1":"ca"}).tidy()
out={"custom":{"coef":a["coef"].to_dict(),"se":a["se"].to_dict()},"pyfixest":{"coef":{str(k):float(v) for k,v in b["Estimate"].items()},"se":{str(k):float(v) for k,v in b["Std. Error"].items()}}}
json.dump(out,open("tabs/estimator_validation.json","w"),indent=1); print(json.dumps(out))
