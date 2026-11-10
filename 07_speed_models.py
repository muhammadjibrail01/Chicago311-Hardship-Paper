import json, sys
from prep import get; from fe import feols
r=get(["lhrs","prank","slow"])
T=["ty","ym","dow","hod"]
specs={"(1)":(["hs"],["ty"]),"(2)":(["hs"],T),"(3)":(["hs"],T+["chan"]),"(4)":(["hs","lwl"],T+["chan"]),
       "(5)":(["hs","lwl","ldens","dist_loop_km","lpop"],T+["chan"]),"(6)":(["hs","lwl"],T+["chan","wy"])}
out={}
for y in ["lhrs","prank","slow"]:
    for s,(X,F) in specs.items():
        m=feols(r,y,X,fes=F)
        out[f"{y}|{s}"]={"coef":m["coef"].to_dict(),"se":m["se"].to_dict(),"p":m["p"].to_dict(),"n":m["n"],"G":m["G"],"r2w":m["r2w"],"ymean":m["ymean"]}
        print(y,s,round(m["coef"]["hs"],4),round(m["se"]["hs"],4),round(m["p"]["hs"],4),flush=True)
# quartile dummies, spec 4
for q in [2,3,4]: r[f"q{q}"]=(r.hq==q).astype("float32")
for y in ["lhrs","prank","slow"]:
    m=feols(r,y,["q2","q3","q4","lwl"],fes=T+["chan"])
    out[f"{y}|quart"]={"coef":m["coef"].to_dict(),"se":m["se"].to_dict(),"p":m["p"].to_dict(),"n":m["n"],"G":m["G"],"r2w":m["r2w"],"ymean":m["ymean"]}
    print(y,"quartiles",{k:round(v,4) for k,v in m["coef"].items()},{k:round(v,4) for k,v in m["se"].items()},flush=True)
json.dump(out,open("tabs/reg_speed.json","w"),default=float)
