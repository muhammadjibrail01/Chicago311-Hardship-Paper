import json, gc, warnings, numpy as np, pandas as pd, pyarrow.parquet as pq
warnings.filterwarnings("ignore")
from prep import get; from fe import feols
OUT={}
def save(): json.dump(OUT,open("tabs/an2.json","w"),default=float)
ca=pd.read_csv("ca.csv").set_index("ca")
# ---------- A. SURVIVAL ----------
try:
    from lifelines import CoxPHFitter, KaplanMeierFitter
    r=get(["dup","completed","canceled","unresolved","hrs","created"],filt="resident"); r=r[~r.dup]
    ext=pd.Timestamp("2026-09-23")
    dur=np.where(r.unresolved,(ext-r.created).dt.total_seconds()/3600,r.hrs); ev=r.completed.astype(int).values
    r["dur"]=np.maximum(dur,1e-3)/24; r["ev"]=ev; r=r[np.isfinite(r.dur)]
    KM=[]; 
    for t in ["Graffiti Removal Request","Street Light Out Complaint","Pothole in Street Complaint","Rodent Baiting/Rat Complaint"]:
        d=r[r.type==t]
        for q in [1,2,3,4]:
            s=d[d.hq==q]; k=KaplanMeierFitter().fit(s.dur,s.ev)
            grid=np.arange(0,90.5,0.5); sf=k.survival_function_at_times(grid).values
            KM.append(pd.DataFrame({"type":t,"hq":q,"day":grid,"S":sf}))
            OUT[f"km_med|{t}|{q}"]=float(k.median_survival_time_)
    pd.concat(KM).to_csv("tabs/km.csv",index=False)
    s=r.sample(120_000,random_state=7).copy()
    for c in ["digital","alderman"]: s["c_"+c]=(s.chan==c).astype(float)
    for y in range(2020,2025): s[f"y{y}"]=(s.year==y).astype(float)
    for q in [2,3,4]: s[f"q{q}"]=(s.hq==q).astype(float)
    base=["dur","ev","type","ca","c_digital","c_alderman","lwl"]+[f"y{y}" for y in range(2020,2025)]
    s["type"]=s.type.astype(str)
    for nm,X in [("cox_hs",["hs"]),("cox_q",["q2","q3","q4"])]:
        cph=CoxPHFitter().fit(s[base+X],"dur","ev",strata=["type"],cluster_col="ca")
        sm=cph.summary
        OUT[nm]={v:{"hr":float(sm.loc[v,"exp(coef)"]),"lo":float(sm.loc[v,"exp(coef) lower 95%"]),"hi":float(sm.loc[v,"exp(coef) upper 95%"]),"p":float(sm.loc[v,"p"])} for v in X+["c_digital","c_alderman","lwl"]}
        OUT[nm]["n"]=len(s); OUT[nm]["events"]=int(s.ev.sum())
        print(nm,{k:(round(v["hr"],3),round(v["p"],4)) for k,v in OUT[nm].items() if isinstance(v,dict)},flush=True)
    print("KM medians (days):",{k.split("|",1)[1]:round(v,2) for k,v in OUT.items() if k.startswith("km_med")},flush=True)
    OUT["surv_n"]=len(r); OUT["surv_censored_share"]=float(1-r.ev.mean()); save(); del r,s; gc.collect()
except Exception as e: print("SURVIVAL FAILED",repr(e))
# ---------- B. DECOMPOSITION Q4 vs Q1 ----------
try:
    r=pq.read_table("core.parquet",columns=["type","year","chan","lhrs","ca","hq","speed_s","dept"],read_dictionary=["type","chan","dept"]).to_pandas()
    r=r[r.speed_s & r.hq.isin([1,4])]
    r["cell"]=r.type.astype(str)+"|"+r.year.astype(str)+"|"+r.chan.astype(str); r["cty"]=r.type.astype(str)+"|"+r.year.astype(str)
    dept_of=r.groupby("cell",observed=True).dept.first().astype(str)
    def build(key):
        a=r.groupby(["hq","ca",key],observed=True).lhrs.agg(["sum","size"]).reset_index(); return a
    def decomp(a,key,mult=None):
        res={}
        a=a.copy()
        if mult is not None: a["w"]=a.ca.map(mult).fillna(0); a["sum"]*=a.w; a["size"]*=a.w
        c=a.groupby(["hq",key])[["sum","size"]].sum().reset_index()
        p=c.pivot(index=key,columns="hq",values=["sum","size"]).fillna(0)
        n1,n4=p[("size",1)],p[("size",4)]; s1,s4=p[("sum",1)],p[("sum",4)]
        tot=s4.sum()/n4.sum()-s1.sum()/n1.sum()
        sup=(n1>0)&(n4>0); w1=n1[sup]/n1[sup].sum(); w4=n4[sup]/n4[sup].sum(); m1=s1[sup]/n1[sup]; m4=s4[sup]/n4[sup]
        comp=((w4-w1)*m1).sum(); within=(w4*(m4-m1)).sum()
        return tot,comp,within,1-(n1[sup].sum()+n4[sup].sum())/(n1.sum()+n4.sum()),(w4*(m4-m1))
    A=build("cell"); B=build("cty")
    tot,comp,within,off,wc=decomp(A,"cell"); _,comp_ty,within_ty,_,_=decomp(B,"cty")
    OUT["decomp"]={"total":tot,"comp_full":comp,"within_full":within,"offsupport":off,"comp_type":comp_ty,"comp_chan_increment":comp-comp_ty,"within_ty":within_ty}
    wd=wc.groupby(dept_of.reindex(wc.index).values).sum(); OUT["decomp_dept"]=wd.to_dict()
    rng=np.random.default_rng(3); cas={q:ca.index[ca.hq==q].values for q in [1,4]}; bs=[]
    for b in range(500):
        mult={}
        for q in [1,4]:
            dr=rng.choice(cas[q],len(cas[q]),replace=True)
            for k,v in pd.Series(dr).value_counts().items(): mult[k]=v
        t1,c1,w1_,_,_=decomp(A,"cell",mult); _,c2,_,_,_=decomp(B,"cty",mult); bs.append((t1,c1,w1_,c2,c1-c2))
    bs=np.array(bs); OUT["decomp_ci"]={k:[float(np.percentile(bs[:,i],2.5)),float(np.percentile(bs[:,i],97.5))] for i,k in enumerate(["total","comp_full","within_full","comp_type","comp_chan_increment"])}
    print("DECOMP",{k:round(v,4) for k,v in OUT["decomp"].items()},OUT["decomp_ci"],{k[:20]:round(v,4) for k,v in OUT["decomp_dept"].items()},flush=True)
    save(); del r,A,B; gc.collect()
except Exception as e: print("DECOMP FAILED",repr(e))
# ---------- C. CA-ADJUSTED INDICES ----------
try:
    adj={}
    d=get(["lhrs","slow"])
    for y in ["lhrs","slow"]:
        if y=="slow": d["slow"]=100*d.slow
        m=feols(d,y,["lwl"],fes=["ty","ym","dow","hod","chan"])
        adj["adj_"+y]=pd.Series(m["resid"]).groupby(d.loc[m["idx"],"ca"].values).mean(); del m; gc.collect()
    adj["n_speed"]=d.groupby("ca").size(); adj["slow_n"]=(d.slow/100).groupby(d.ca).sum(); del d; gc.collect()
    d=get(["recur30"]); d["recur30"]=100*d.recur30; m=feols(d,"recur30",["lwl"],fes=["ty","ym","dow","hod","chan"])
    adj["adj_recur30"]=pd.Series(m["resid"]).groupby(d.loc[m["idx"],"ca"].values).mean(); del d,m; gc.collect()
    A=pd.DataFrame(adj); A.index.name="ca"; A.to_csv("tabs/ca_adj.csv"); print("adjusted indices built",A.describe().round(3).loc[["mean","std","min","max"]].to_dict(),flush=True)
except Exception as e: print("ADJ FAILED",repr(e))
# ---------- D. SPATIAL ----------
try:
    import geopandas as gpd, libpysal, spreg
    from esda.moran import Moran, Moran_Local
    import statsmodels.api as sm
    g=gpd.read_file("ca.gpkg").sort_values("ca").reset_index(drop=True)
    o=pd.read_csv("ca_out.csv").set_index("ca"); A=pd.read_csv("tabs/ca_adj.csv").set_index("ca")
    g=g.join(A,on="ca").join(o[["req_pc","digital_share","city_share","phone_share","ald_share"]],on="ca")
    g["hs_ca"]=(g.hardship-g.hardship.mean())/g.hardship.std(); g["zblack"]=(g.pct_black-g.pct_black.mean())/g.pct_black.std()
    w=libpysal.weights.Queen.from_dataframe(g,use_index=False); w.transform="r"; OUT["w_islands"]=list(map(int,w.islands))
    for v in ["hardship","adj_lhrs","adj_slow","adj_recur30","digital_share","req_pc","pct_black"]:
        mi=Moran(g[v].values,w,permutations=9999); OUT[f"moran|{v}"]={"I":mi.I,"p":mi.p_sim,"z":mi.z_sim}
    lm=Moran_Local(g.adj_lhrs.values,w,permutations=9999,seed=1)
    lab=np.array(["ns"]*len(g),dtype=object); sig=lm.p_sim<0.05
    for qv,nm in [(1,"High-High"),(2,"Low-High"),(3,"Low-Low"),(4,"High-Low")]: lab[sig&(lm.q==qv)]=nm
    g["lisa"]=lab; OUT["lisa_counts"]=pd.Series(lab).value_counts().to_dict()
    OUT["lisa_members"]={k:g.loc[g.lisa==k,"name"].str.title().tolist() for k in ["High-High","Low-Low","High-Low","Low-High"]}
    print("MORAN",{k:(round(v["I"],3),round(v["p"],4)) for k,v in OUT.items() if k.startswith("moran")},OUT["lisa_counts"],flush=True)
    y=g[["adj_lhrs"]].values
    for nm,cols in [("m1",["hs_ca"]),("m2",["hs_ca","zblack"])]:
        X=g[cols].values
        ols=spreg.OLS(y,X,w=w,spat_diag=True,moran=True,robust="white",name_x=cols)
        lag=spreg.ML_Lag(y,X,w,name_x=cols); err=spreg.ML_Error(y,X,w,name_x=cols)
        OUT[f"sp|{nm}"]={"ols_b":list(map(float,ols.betas.flatten())),"ols_se":list(map(float,ols.std_err)),"ols_r2":float(ols.r2),
          "moran_res":[float(ols.moran_res[0]),float(ols.moran_res[2])],"lm_lag":[float(ols.lm_lag[0]),float(ols.lm_lag[1])],"lm_err":[float(ols.lm_error[0]),float(ols.lm_error[1])],
          "rlm_lag":[float(ols.rlm_lag[0]),float(ols.rlm_lag[1])],"rlm_err":[float(ols.rlm_error[0]),float(ols.rlm_error[1])],
          "lag_b":list(map(float,lag.betas.flatten())),"lag_se":list(map(float,lag.std_err)),"lag_aic":float(lag.aic),
          "err_b":list(map(float,err.betas.flatten())),"err_se":list(map(float,err.std_err)),"err_aic":float(err.aic),"ols_aic":float(ols.aic) if hasattr(ols,"aic") else None}
        # wild bootstrap (restricted, Rademacher) for hs_ca
        Xc=sm.add_constant(g[cols]); fit=sm.OLS(g.adj_lhrs,Xc).fit(cov_type="HC3")
        Xr=Xc.drop(columns="hs_ca"); fr=sm.OLS(g.adj_lhrs,Xr).fit(); ur=fr.resid.values; yhat=fr.fittedvalues.values
        t0=fit.tvalues["hs_ca"]; rng=np.random.default_rng(11); cnt=0; B=9999
        for b in range(B):
            vs=rng.choice([-1,1],len(g)); yb=yhat+ur*vs; fb=sm.OLS(yb,Xc).fit(cov_type="HC3")
            cnt+= abs(fb.tvalues["hs_ca"])>=abs(t0)
        OUT[f"sp|{nm}"].update({"hc3_b":float(fit.params["hs_ca"]),"hc3_se":float(fit.bse["hs_ca"]),"hc3_p":float(fit.pvalues["hs_ca"]),"wild_p":(cnt+1)/(B+1),"r2":float(fit.rsquared)})
        if nm=="m2": OUT["sp|m2"].update({"zblack_b":float(fit.params["zblack"]),"zblack_se":float(fit.bse["zblack"]),"zblack_p":float(fit.pvalues["zblack"])})
        print("SPATIAL",nm,{k:(np.round(v,4) if not isinstance(v,list) else np.round(v,4).tolist()) for k,v in OUT[f"sp|{nm}"].items()},flush=True)
    g.drop(columns="geometry").to_csv("tabs/ca_spatial.csv",index=False); g.to_file("ca_spatial.gpkg",driver="GPKG"); save()
except Exception as e:
    import traceback; traceback.print_exc(); print("SPATIAL FAILED",repr(e))
# ---------- E. EQUITY ----------
try:
    import statsmodels.api as sm, statsmodels.formula.api as smf
    r=pq.read_table("core.parquet",columns=["type","dept","chan","resident","dup","ca","year"],read_dictionary=["type","chan","dept"]).to_pandas()
    g=pd.read_csv("tabs/ca_spatial.csv").set_index("ca")
    res=r[r.resident&~r.dup]
    cnt=pd.DataFrame({"res":res.groupby("ca").size(),"city":r[r.chan=="city"].groupby("ca").size(),"digital":res[res.chan=="digital"].groupby("ca").size(),
                      "phone":res[res.chan=="phone"].groupby("ca").size(),
                      "bldg311":res[res.dept.astype(str)=="DOB - Buildings"].groupby("ca").size()})
    cnt=cnt.join(g[["pop","hardship","slow_n","bviol","violent","name"]])
    cnt.to_csv("tabs/ca_counts.csv")
    def ci(y,pop,hard):
        o=np.argsort(-hard); y=y[o]; w=pop[o]/pop.sum(); R=np.cumsum(w)-w/2; mu=(w*y).sum()
        return 2*(w*(y-mu)*(R-0.5)).sum()/mu
    P=cnt["pop"].values; H=cnt.hardship.values; rng=np.random.default_rng(5)
    for v in ["res","city","digital","phone","slow_n","bldg311","bviol","violent"]:
        y=(cnt[v]/cnt["pop"]).values; est=ci(y,P,H); bb=[]
        for b in range(2000):
            i=rng.integers(0,len(y),len(y)); bb.append(ci(y[i],P[i],H[i]))
        OUT[f"ci|{v}"]=[est,float(np.percentile(bb,2.5)),float(np.percentile(bb,97.5))]
    print("CONC",{k:np.round(v,3).tolist() for k,v in OUT.items() if k.startswith("ci|")},flush=True)
    # Poisson per-capita reporting at CA x type x year
    a=res.groupby(["ca","type","year"],observed=True).size().rename("y").reset_index()
    grid=pd.MultiIndex.from_product([range(1,78),res.type.cat.categories,range(2019,2025)],names=["ca","type","year"])
    a=a.set_index(["ca","type","year"]).reindex(grid,fill_value=0).reset_index()
    for v in ["hardship","bviol_rate","viol_rate","pct_black","pop"]: a[v]=a.ca.map(ca[v])
    for v in ["hardship","bviol_rate","viol_rate","pct_black"]: a["z_"+v]=(a[v]-ca[v].mean())/ca[v].std()
    a["ty"]=a.type.astype(str)+"|"+a.year.astype(str); a["lp"]=np.log(a["pop"])
    for nm,f in [("p1","y ~ z_hardship + C(ty)"),("p2","y ~ z_hardship + z_bviol_rate + z_viol_rate + C(ty)"),("p3","y ~ z_hardship + z_bviol_rate + z_viol_rate + z_pct_black + C(ty)")]:
        mod=smf.glm(f,data=a,family=sm.families.Poisson(),offset=a.lp).fit(cov_type="cluster",cov_kwds={"groups":a.ca})
        ks=[k for k in mod.params.index if k.startswith("z_")]
        OUT["pois|"+nm]={k:{"irr":float(np.exp(mod.params[k])),"lo":float(np.exp(mod.conf_int().loc[k,0])),"hi":float(np.exp(mod.conf_int().loc[k,1])),"p":float(mod.pvalues[k])} for k in ks}
        OUT["pois|"+nm]["n"]=len(a)
        print("POIS",nm,{k:(round(v["irr"],3),round(v["p"],4)) for k,v in OUT["pois|"+nm].items() if isinstance(v,dict)},flush=True)
    # proactive (city-generated) share, CA x type x year WLS
    b=r.groupby(["ca","type","year"],observed=True).agg(n=("chan","size"),city=("chan",lambda s:(s=="city").sum())).reset_index()
    b=b[b.n>0]; b["cs"]=100*b.city/b.n; b["hs"]=(b.ca.map(ca.hardship)-ca.hardship.mean())/ca.hardship.std()
    b["zb"]=(b.ca.map(ca.bviol_rate)-ca.bviol_rate.mean())/ca.bviol_rate.std(); b["ty"]=b.type.astype(str)+b.year.astype(str)
    for nm,X in [("pro1",["hs"]),("pro2",["hs","zb"])]:
        m=feols(b,"cs",X,fes=["ty"],w="n"); OUT[nm]={"coef":m["coef"].to_dict(),"se":m["se"].to_dict(),"p":m["p"].to_dict(),"ymean":m["ymean"],"n":m["n"]}
        print("PROACTIVE",nm,m["coef"].round(3).to_dict(),m["se"].round(3).to_dict(),round(m["ymean"],2),flush=True)
    # need-adjusted building complaints
    cnt["ratio"]=cnt.bldg311/cnt.bviol; cnt["hq"]=cnt.index.map(ca.hq)
    OUT["bldg_ratio_q"]=cnt.groupby("hq").apply(lambda d:d.bldg311.sum()/d.bviol.sum()).to_dict()
    ll=sm.OLS(np.log(cnt.bldg311/cnt["pop"]),sm.add_constant(pd.DataFrame({"lviol":np.log(cnt.bviol/cnt["pop"]),"hs":(cnt.hardship-ca.hardship.mean())/ca.hardship.std()}))).fit(cov_type="HC3")
    OUT["bldg_loglog"]={"b":ll.params.to_dict(),"se":ll.bse.to_dict(),"p":ll.pvalues.to_dict(),"r2":ll.rsquared}
    print("BLDG ratio by q",{k:round(v,3) for k,v in OUT["bldg_ratio_q"].items()},"loglog",{k:round(v,3) for k,v in ll.params.items()},{k:round(v,3) for k,v in ll.bse.items()},flush=True)
    cnt.to_csv("tabs/ca_counts.csv"); save()
except Exception as e:
    import traceback; traceback.print_exc(); print("EQUITY FAILED",repr(e))
