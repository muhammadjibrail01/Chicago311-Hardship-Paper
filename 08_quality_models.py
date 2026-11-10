import json, gc
from prep import get; from fe import feols
T=["ty","ym","dow","hod","chan"]; out={}
def run(y,d):
    for s,F in [("main",T),("ward",T+["wy"])]:
        m=feols(d,y,["hs","lwl"],fes=F)
        out[f"{y}|{s}"]={"coef":m["coef"].to_dict(),"se":m["se"].to_dict(),"p":m["p"].to_dict(),"n":m["n"],"G":m["G"],"r2w":m["r2w"],"ymean":m["ymean"]}
        print(y,s,"b=%.3f se=%.3f p=%.4f n=%d mean=%.2f"%(m["coef"]["hs"],m["se"]["hs"],m["p"]["hs"],m["n"],m["ymean"]),flush=True)
        del m; gc.collect()
    json.dump(out,open("tabs/reg_quality.json","w"),default=float)
for y in ["canceled","unresolved","adminclose","dup"]:
    r=get([y,"dup"] if y!="dup" else ["dup"],filt="resident")
    if y!="dup": r=r[r.dup==False]
    r[y]=100*r[y].astype("float32"); run(y,r); del r; gc.collect()
for y in ["recur30","recur90"]:
    r=get([y]); r[y]=100*r[y]; run(y,r); del r; gc.collect()
