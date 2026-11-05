import json, gc, numpy as np, pandas as pd
from prep import get; from fe import feols
r=get(["lhrs","hrs"]); ca=pd.read_csv("ca.csv").set_index("ca")
def z(v): s=ca[v]; return r.ca.map((s-s.mean())/s.std()).astype("float32")
for v in ["lowinc","pct_black","pct_hisp","viol_rate","bviol_rate","poverty","unemp","nohs","crowded","dependency"]: r["z_"+v]=z(v)
r["z_lpci"]=r.ca.map((np.log(ca.pci)-np.log(ca.pci).mean())/np.log(ca.pci).std()).astype("float32")
T=["ty","ym","dow","hod","chan"]; out={}
def run(k,d,X,F=T,cl="ca",w=None,v="hs",y="lhrs"):
    m=feols(d,y,X,fes=F,cluster=cl,w=w)
    out[k]={"coef":m["coef"].to_dict(),"se":m["se"].to_dict(),"p":m["p"].to_dict(),"n":m["n"],"G":m["G"]}
    print(k,{a:f"{m['coef'][a]:.4f} ({m['se'][a]:.4f})" for a in X if a!="lwl"},m["n"],flush=True)
    json.dump(out,open("tabs/reg_rob.json","w"),default=float)
run("baseline",r,["hs","lwl"])
run("race",r,["hs","z_pct_black","z_pct_hisp","lwl"])
run("race_only",r,["z_pct_black","z_pct_hisp","lwl"])
run("lowinc_acs",r,["z_lowinc","lwl"])
run("hs+lowinc",r,["hs","z_lowinc","lwl"])
run("crime",r,["hs","z_viol_rate","lwl"])
run("need_bviol",r,["hs","z_bviol_rate","lwl"])
for c in ["poverty","unemp","nohs","crowded","dependency","lpci"]: run("comp_"+c,r,["z_"+c,"lwl"])
run("excl2020",r[r.year!=2020],["hs","lwl"])
run("excl_subminute",r[r.hrs>1/60],["hs","lwl"])
run("excl_downtown",r[~r.ca.isin([8,32,33])],["hs","lwl"])
r["lraw"]=np.log1p(r.hrs.clip(lower=0)); run("unwinsorized",r,["hs","lwl"],y="lraw")
run("cluster_ward",r[r.ward>0],["hs","lwl"],cl="ward")
r["wca"]=(1/r.groupby("ca").ca.transform("size")).astype("float64"); run("ca_equal_weight",r,["hs","lwl"],w="wca")
run("tyc_fe",r,["hs","lwl"],F=["tyc","ym","dow","hod"])
r["q4"]=(r.hq==4).astype("float32"); run("q4_vs_q1",r[r.hq.isin([1,4])],["q4","lwl"])
run("excl_longprog",r[~r.type.isin(["Tree Planting Request","Sidewalk Inspection Request"])],["hs","lwl"])
