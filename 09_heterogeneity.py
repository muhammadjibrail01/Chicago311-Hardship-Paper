import json, gc, numpy as np, pandas as pd
from prep import get; from fe import feols
r=get(["lhrs","slow","dept"]); out={}
def save(): json.dump(out,open("tabs/reg_het.json","w"),default=float)
def rec(k,m,v): out[k]={"coef":m["coef"][v] if isinstance(v,str) else m["coef"][v].to_dict(),"se":m["se"][v] if isinstance(v,str) else m["se"][v].to_dict(),
                        "p":m["p"][v] if isinstance(v,str) else m["p"][v].to_dict(),"n":m["n"],"ymean":m["ymean"]}
# by type
for t,d in r.groupby("type",observed=True):
    m=feols(d,"lhrs",["hs","lwl"],fes=["ym","dow","hod","chan"]); rec(f"type|{t}",m,"hs")
    out[f"type|{t}"]["med_hrs"]=float(np.expm1(d.lhrs.median())); out[f"type|{t}"]["dept"]=str(d.dept.iloc[0])
save(); print("types done",flush=True)
# by department
for dp,d in r.groupby("dept",observed=True):
    if len(d)<1000: continue
    for y in ["lhrs","slow"]:
        m=feols(d,y,["hs","lwl"],fes=["ty","ym","dow","hod","chan"]); rec(f"dept|{dp}|{y}",m,"hs")
        print(dp[:25],y,round(m["coef"]["hs"],4),round(m["se"]["hs"],4),m["n"],flush=True)
save()
# year-by-year gradient
yrs=list(range(2019,2025))
for y in yrs: r[f"hs_{y}"]=(r.hs*(r.year==y)).astype("float32")
for y in ["lhrs","slow"]:
    m=feols(r,y,[f"hs_{x}" for x in yrs]+["lwl"],fes=["ty","ym","dow","hod","chan"]); rec(f"year|{y}",m,[f"hs_{x}" for x in yrs])
    print("year",y,{k:round(v,3) for k,v in m["coef"].items()},flush=True)
save(); r.drop(columns=[f"hs_{x}" for x in yrs],inplace=True); gc.collect()
# channel: main effects and interactions
for c in ["digital","alderman"]: r[f"c_{c}"]=(r.chan==c).astype("float32"); r[f"hsX{c}"]=(r.hs*r[f"c_{c}"]).astype("float32")
m=feols(r,"lhrs",["hs","c_digital","c_alderman","hsXdigital","hsXalderman","lwl"],fes=["ty","ym","dow","hod"]); rec("chan|lhrs",m,["hs","c_digital","c_alderman","hsXdigital","hsXalderman","lwl"])
print("chan",{k:round(v,4) for k,v in m["coef"].items()},{k:round(v,4) for k,v in m["se"].items()},flush=True)
m=feols(r,"lhrs",["hs","c_digital","c_alderman","hsXdigital","hsXalderman","lwl"],fes=["ty","ym","dow","hod","wy"]); rec("chan|lhrs|ward",m,["hs","c_digital","c_alderman","hsXdigital","hsXalderman","lwl"])
print("chan ward",{k:round(v,4) for k,v in m["coef"].items()},{k:round(v,4) for k,v in m["se"].items()},flush=True)
save()
