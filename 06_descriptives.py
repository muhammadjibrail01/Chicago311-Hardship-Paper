import pandas as pd, numpy as np, pyarrow.parquet as pq
ca=pd.read_csv("ca.csv")
cols=["type","chan","resident","dup","hrs","lhrs","slow","speed_s","canceled","unresolved","adminclose","recur30","recur90","ca","hq","year"]
r=pq.read_table("core.parquet",columns=cols,read_dictionary=["type","chan"]).to_pandas()
res=r[r.resident]; rnd=res[~res.dup]; sp=r[r.speed_s]
# CA-level aggregates
g=pd.DataFrame({
 "n_all":r.groupby("ca").size(),"n_res":res.groupby("ca").size(),
 "city_share":r.groupby("ca").chan.apply(lambda s:(s=="city").mean()),
 "digital_share":res.groupby("ca").chan.apply(lambda s:(s=="digital").mean()),
 "ald_share":res.groupby("ca").chan.apply(lambda s:(s=="alderman").mean()),
 "phone_share":res.groupby("ca").chan.apply(lambda s:(s=="phone").mean()),
 "dup_share":res.groupby("ca").dup.mean(),
 "med_hrs":sp.groupby("ca").hrs.median(),"slow":sp.groupby("ca").slow.mean(),
 "cancel":rnd.groupby("ca").canceled.mean(),"unres":rnd.groupby("ca").unresolved.mean(),
 "recur30":sp.groupby("ca").recur30.mean(),"recur90":sp.groupby("ca").recur90.mean()}).reset_index()
m=ca.merge(g,on="ca"); m["req_pc"]=1000*m.n_res/m["pop"]/6
m.to_csv("ca_out.csv",index=False)
# Table 2: CA characteristics by quartile
t2=m.groupby("hq").agg(n_ca=("ca","size"),hardship=("hardship","mean"),pci=("pci","mean"),poverty=("poverty","mean"),unemp=("unemp","mean"),
  nohs=("nohs","mean"),lowinc=("lowinc","mean"),pct_black=("pct_black","mean"),pct_hisp=("pct_hisp","mean"),pct_nhwhite=("pct_nhwhite","mean"),
  pop=("pop","sum"),density=("density","mean"),viol_rate=("viol_rate","mean"),bviol_rate=("bviol_rate","mean"),dist=("dist_loop_km","mean"))
t2.loc["All"]=[77,m.hardship.mean(),m.pci.mean(),m.poverty.mean(),m.unemp.mean(),m.nohs.mean(),m.lowinc.mean(),m.pct_black.mean(),m.pct_hisp.mean(),m.pct_nhwhite.mean(),m["pop"].sum(),m.density.mean(),m.viol_rate.mean(),m.bviol_rate.mean(),m.dist_loop_km.mean()]
t2.to_csv("tabs/t2_ca_by_q.csv"); print(t2.round(1).T.to_string())
# Table 3: request-level outcomes by quartile
def q(df,fn): return df.groupby("hq").apply(fn)
pop_q=m.groupby("hq")["pop"].sum()
t3=pd.DataFrame({
 "resident_requests":res.groupby("hq").size(),
 "req_per_1000_yr":1000*res.groupby("hq").size()/pop_q/6,
 "city_generated_%":100*r.groupby("hq").chan.apply(lambda s:(s=="city").mean()),
 "digital_%":100*res.groupby("hq").chan.apply(lambda s:(s=="digital").mean()),
 "alderman_%":100*res.groupby("hq").chan.apply(lambda s:(s=="alderman").mean()),
 "median_hours":sp.groupby("hq").hrs.median(),
 "mean_log_hours":sp.groupby("hq").lhrs.mean(),
 "slower_than_type_median_%":100*sp.groupby("hq").slow.mean(),
 "canceled_%":100*rnd.groupby("hq").canceled.mean(),
 "unresolved_%":100*rnd.groupby("hq").unresolved.mean(),
 "admin_close_%":100*rnd.groupby("hq").adminclose.mean(),
 "duplicate_%":100*res.groupby("hq").dup.mean(),
 "recur30_%":100*sp.groupby("hq").recur30.mean(),
 "recur90_%":100*sp.groupby("hq").recur90.mean()})
allrow={"resident_requests":len(res),"req_per_1000_yr":1000*len(res)/m["pop"].sum()/6,"city_generated_%":100*(r.chan=="city").mean(),
 "digital_%":100*(res.chan=="digital").mean(),"alderman_%":100*(res.chan=="alderman").mean(),"median_hours":sp.hrs.median(),"mean_log_hours":sp.lhrs.mean(),
 "slower_than_type_median_%":100*sp.slow.mean(),"canceled_%":100*rnd.canceled.mean(),"unresolved_%":100*rnd.unresolved.mean(),"admin_close_%":100*rnd.adminclose.mean(),
 "duplicate_%":100*res.dup.mean(),"recur30_%":100*sp.recur30.mean(),"recur90_%":100*sp.recur90.mean()}
t3.loc["All"]=allrow; t3.to_csv("tabs/t3_outcomes_by_q.csv"); print(t3.round(2).T.to_string())
# sample-flow numbers
print("speed n",len(sp),"resident nondup",len(rnd))
