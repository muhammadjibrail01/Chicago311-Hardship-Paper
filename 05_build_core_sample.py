from common import *
import gc
r=load(["type","dept","status","origin","created","closed","dup","ca","ward","addr","lat","lon"])
DEPTS={"Streets and Sanitation","CDOT - Department of Transportation","DWM - Department of Water Management","Animal Care and Control","DOB - Buildings"}
EXCL={"Tree Trim Request (NO LONGER BEING ACCEPTED)","Water Lead Test Kit Request","Water Lead Test Visit Request","Shared Cost Sidewalk Program Request","Vehicle Parked in Bike Lane Complaint"}
tp=pd.read_csv("tabs/type_profile.csv")
mode_dept=r.groupby("type",observed=True).dept.agg(lambda s:s.value_counts().index[0])
tp["dept_full"]=tp.type.map(mode_dept)
core=tp[(tp.dept_full.isin(DEPTS))&(tp.n>=10000)&(~tp.type.isin(EXCL))].type.tolist()
r=r[r.type.isin(core)]; r["type"]=r.type.cat.remove_unused_categories(); gc.collect()
PHONE={"Phone Call","Phone","Walk-in","Mail","Fax"}
DIGI={"Internet","Web","Mobile Device","E-Mail","Social Media","Open311","Open311 Interface","Spot311 Interface","SPOT311"}
ALD={"Alderman's Office","ALDERMAN","State Representatives","Mayor's Office","Budget Town Hall Meeting","FY25 Budget Engagement"}
def ch(o): return "phone" if o in PHONE else "digital" if (o in DIGI or o.startswith("spot-open311")) else "alderman" if o in ALD else "city"
cm={c:ch(c) for c in r.origin.cat.categories}
r["chan"]=pd.Categorical(r.origin.map(cm).astype(str),categories=["phone","digital","alderman","city"]); r.drop(columns="origin",inplace=True)
st=r.status.astype(str); r["completed"]=(st=="Completed").values; r["canceled"]=(st=="Canceled").values; r["unresolved"]=(st=="Open").values; del st
r["hrs"]=((r.closed-r.created).dt.total_seconds()/3600).astype("float32")
r["year"]=r.created.dt.year.astype("int16"); r["ym"]=((r.year-2019)*12+r.created.dt.month-1).astype("int16")
r["dow"]=r.created.dt.dayofweek.astype("int8"); r["hod"]=r.created.dt.hour.astype("int8")
r["wk"]=((r.created-pd.Timestamp("2019-01-01")).dt.days//7).astype("int16")
r["resident"]=(r.chan!="city").values
sp=(r.resident & ~r.dup & r.completed & (r.hrs>=0)).values; r["speed_s"]=sp
cap=r[sp].groupby("type",observed=True).hrs.quantile(.99)
r["hrs_w"]=np.minimum(r.hrs.values, r.type.map(cap).astype("float32").values)
r["lhrs"]=np.log1p(r.hrs_w).astype("float32")
pr=r.loc[sp].groupby(["type","year"],observed=True).hrs.rank(pct=True)*100
r["prank"]=np.float32(np.nan); r.loc[sp,"prank"]=pr.astype("float32"); del pr
med=r.loc[sp].groupby(["type","year"],observed=True).hrs.transform("median")
r["slow"]=np.float32(np.nan); r.loc[sp,"slow"]=(r.loc[sp,"hrs"]>med).astype("float32"); del med
r["adminclose"]=(r.hrs<=1/60).values
base=(r.resident & ~r.dup).values
k=(r.type.cat.codes.astype(np.int64)*1000+r.ca.astype(np.int64))*1000+r.wk.astype(np.int64)
wl=k[base].value_counts(); r["lwl"]=np.log(k.map(wl).fillna(1).astype("float32")); del k,wl
gc.collect()
# recurrence
gkey=pd.util.hash_pandas_object(pd.DataFrame({"t":r.type.cat.codes.values,"a":r.addr.values}),index=False).values
r["ga"]=pd.factorize(gkey)[0].astype(np.int64); del gkey; r.drop(columns="addr",inplace=True); gc.collect()
cnt=r.ga.value_counts(); big=set(cnt[cnt>cnt.quantile(.9995)].index); print("placeholder groups",len(big),"reqs",int(cnt[list(big)].sum()))
T0=np.datetime64("2019-01-01")
cmin=((r.created.values-T0)//np.timedelta64(1,"m")).astype(np.int64)
res_idx=np.where(r.resident.values)[0]
key=(r.ga.values[res_idx]<<32)|cmin[res_idx]; o=np.argsort(key,kind="stable"); key=key[o]; ctime=r.created.values[res_idx][o]; gsorted=r.ga.values[res_idx][o]
del o,res_idx
qi=np.where((r.completed & ~r.dup & r.resident & r.closed.notna()).values)[0]
clo=r.closed.values[qi]; qk=(r.ga.values[qi]<<32)|((clo-T0)//np.timedelta64(1,"m")).astype(np.int64)
p=np.searchsorted(key,qk,side="right"); ok=p<len(key); pp=np.where(ok,p,0)
same=ok&(gsorted[pp]==r.ga.values[qi]); gap=(ctime[pp]-clo)/np.timedelta64(1,"D")
isbig=np.isin(r.ga.values[qi],list(big))
for d in [30,90]:
    v=np.where(same&(gap<=d),1.0,0.0).astype("float32")
    v[clo>np.datetime64("2024-12-31")-np.timedelta64(d,"D")]=np.nan; v[isbig]=np.nan
    col=np.full(len(r),np.nan,dtype="float32"); col[qi]=v; r[f"recur{d}"]=col
del key,ctime,gsorted,qk,p,pp,same,gap; gc.collect()
ca=pd.read_csv("ca.csv").set_index("ca")
r["hardship"]=r.ca.map(ca.hardship).astype("float32"); r["hq"]=r.ca.map(ca.hq).astype("int8")
r.to_parquet("core.parquet",compression="zstd")
print(f"core types {len(core)}; core rows {len(r):,}; resident {r.resident.sum():,}; speed sample {sp.sum():,}")
print("speed-sample means:", r.loc[sp,["lhrs","slow","recur30","recur90"]].mean().round(3).to_dict())
b=r[base]; print("resident non-dup: canceled %.3f unresolved %.3f adminclose %.3f"%(b.canceled.mean(),b.unresolved.mean(),b.adminclose.mean()))
print(r.chan.value_counts().to_dict())
pd.Series(core).to_csv("tabs/core_types.csv",index=False)
