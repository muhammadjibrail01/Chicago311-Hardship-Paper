import json, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,"axes.titlesize":9,"axes.labelsize":8.5,"axes.spines.top":False,"axes.spines.right":False,"savefig.dpi":220,"savefig.bbox":"tight","legend.frameon":False})
J=lambda f: json.load(open(f"tabs/{f}.json"))
S,Q,H,R,A=J("reg_speed"),J("reg_quality"),J("reg_het"),J("reg_rob"),J("an2")
QC=["#2c7bb6","#abd9e9","#fdae61","#d7191c"]; QL=["Q1 (lowest hardship)","Q2","Q3","Q4 (highest hardship)"]
DS={"Streets and Sanitation":"Streets & Sanitation","CDOT - Department of Transportation":"Transportation (CDOT)","DWM - Department of Water Management":"Water Management (DWM)","Animal Care and Control":"Animal Care & Control","DOB - Buildings":"Buildings (DOB)"}
DC=dict(zip(DS.values(),["#1b9e77","#d95f02","#7570b3","#e7298a","#66a61e"]))
pct=lambda b: 100*(np.exp(b)-1)
g=gpd.read_file("ca_spatial.gpkg")
# ---------- Fig 1: conceptual framework
fig,ax=plt.subplots(figsize=(7.6,2.5)); ax.set_xlim(0,10); ax.set_ylim(0,3.5); ax.axis("off")
st=[("Neighborhood\nconditions","Objective need\n(violations, crime)","Tests H5"),("Reporting","Volume per capita;\nchannel mix","Tests H3, H5"),("Intake &\ntriage","Request type, timing,\nduplicate linking","Held fixed (FE)"),
    ("Dispatch &\nqueueing","Ward-based crews\nvs. central units","Tests H1, H4"),("Resolution\n& quality","Closure, cancellation,\nrecurrence","Tests H2")]
for i,(t,s_,h) in enumerate(st):
    x=0.1+i*2; ax.add_patch(FancyBboxPatch((x,1.95),1.72,1.05,boxstyle="round,pad=0.04",fc="#eef3f8",ec="#34495e",lw=1))
    ax.text(x+0.86,2.47,t,ha="center",va="center",fontsize=8,weight="bold")
    ax.text(x+0.86,1.35,s_,ha="center",va="center",fontsize=6.8,color="#333")
    ax.text(x+0.86,0.62,h,ha="center",va="center",fontsize=7.2,color="#c0392b",weight="bold")
    if i<4: ax.annotate("",xy=(x+2.02,2.47),xytext=(x+1.8,2.47),arrowprops=dict(arrowstyle="-|>",color="#34495e",lw=1.2))
ax.text(5,3.35,"Stages at which neighborhood hardship can shape 311 service outcomes",ha="center",fontsize=9,weight="bold")
fig.savefig("figs/fig1.png"); plt.close()
# ---------- Fig 2: maps
fig,axs=plt.subplots(2,2,figsize=(7,8.2)); axs=axs.ravel()
g["adj_pct"]=pct(g.adj_lhrs); g["dig"]=100*g.digital_share
for ax,(col,cm,tt,lab) in zip(axs[:3],[("hardship","YlOrRd","(a) Hardship Index, 2008–2012","Index (1–98)"),("adj_pct","RdBu_r","(b) Type-adjusted completion time","% vs. citywide average"),("dig","Blues","(c) Web and app reporting share","% of resident requests")]):
    vmax=None; kw={}
    if col=="adj_pct": v=np.nanmax(np.abs(g[col])); kw=dict(vmin=-v,vmax=v)
    g.plot(column=col,cmap=cm,ax=ax,edgecolor="white",linewidth=0.3,legend=True,legend_kwds={"shrink":0.6,"label":lab},**kw)
    ax.set_title(tt,loc="left"); ax.axis("off")
cols={"High-High":"#d7191c","Low-Low":"#2c7bb6","High-Low":"#fdae61","Low-High":"#abd9e9","ns":"#e6e6e6"}
g.plot(color=g.lisa.map(cols),ax=axs[3],edgecolor="white",linewidth=0.3); axs[3].axis("off"); axs[3].set_title("(d) Local Moran clusters of adjusted time",loc="left")
axs[3].legend(handles=[Patch(fc=cols[k],label=f"{k} ({int((g.lisa==k).sum())})" if k!="ns" else f"Not significant ({int((g.lisa=='ns').sum())})") for k in ["High-High","Low-Low","ns"]],loc="lower left",fontsize=7.5)
fig.tight_layout(); fig.savefig("figs/fig2.png"); plt.close()
# ---------- Fig 3: CA scatter
fig,axs=plt.subplots(1,3,figsize=(7.4,2.7))
g["rec"]=g.adj_recur30
for ax,(x,y,xl,yl) in zip(axs,[("hardship","adj_pct","Hardship Index","Adjusted completion time (%)"),("pct_black","adj_pct","Black residents (%)","Adjusted completion time (%)"),("hardship","rec","Hardship Index","Adjusted 30-day recurrence (pp)")]):
    ax.scatter(g[x],g[y],s=g.n_speed/2500,c=[QC[q-1] for q in g.hq],alpha=.8,edgecolor="k",linewidth=.3)
    b=np.polyfit(g[x],g[y],1,w=np.sqrt(g.n_speed)); xs=np.linspace(g[x].min(),g[x].max(),50); ax.plot(xs,np.polyval(b,xs),color="k",lw=1)
    rr=np.corrcoef(g[x],g[y])[0,1]; ax.text(.03,.95,f"r = {rr:.2f}",transform=ax.transAxes,va="top",fontsize=8)
    ax.axhline(0,color="gray",lw=.5,ls=":"); ax.set_xlabel(xl); ax.set_ylabel(yl)
fig.legend(handles=[Line2D([],[],marker="o",ls="",color=c,label=l) for c,l in zip(QC,["Q1 (lowest hardship)","Q2","Q3","Q4 (highest hardship)"])],fontsize=7.5,loc="lower center",ncol=4,bbox_to_anchor=(0.5,-0.04))
fig.tight_layout(rect=[0,0.07,1,1]); fig.savefig("figs/fig3.png"); plt.close()
# ---------- Fig 4: slower not worse
fig,axs=plt.subplots(2,1,figsize=(6.4,4.9),gridspec_kw={"height_ratios":[3,6]})
sp=[("Completion time (% change)","lhrs",lambda b:pct(b)),("Slower than type–year median (pp)","slow",lambda b:100*b),("Within-type percentile rank (points)","prank",lambda b:b)]
for i,(lab,k,f) in enumerate(sp):
    for j,(s,mk,off,c) in enumerate([("(4)","o",-.12,"#c0392b"),("(6)","s",.12,"#7f8c8d")]):
        b,se=S[f"{k}|{s}"]["coef"]["hs"],S[f"{k}|{s}"]["se"]["hs"]
        axs[0].errorbar(f(b),i+off,xerr=[[f(b)-f(b-1.96*se)],[f(b+1.96*se)-f(b)]],fmt=mk,color=c,ms=4,capsize=2)
axs[0].set_yticks(range(3)); axs[0].set_yticklabels([s[0] for s in sp]); axs[0].invert_yaxis(); axs[0].axvline(0,color="k",lw=.6); axs[0].set_title("(a) Speed",loc="left")
ql=[("Canceled","canceled"),("Still open (unresolved)","unresolved"),("Closed within one minute","adminclose"),("Duplicate of an open request","dup"),("Re-reported within 30 days","recur30"),("Re-reported within 90 days","recur90")]
for i,(lab,k) in enumerate(ql):
    for s,mk,off,c in [("main","o",-.12,"#c0392b"),("ward","s",.12,"#7f8c8d")]:
        b,se=Q[f"{k}|{s}"]["coef"]["hs"],Q[f"{k}|{s}"]["se"]["hs"]; axs[1].errorbar(b,i+off,xerr=1.96*se,fmt=mk,color=c,ms=4,capsize=2)
axs[1].set_yticks(range(6)); axs[1].set_yticklabels([f"{l} [mean {Q[k+'|main']['ymean']:.1f}%]" for l,k in ql]); axs[1].invert_yaxis(); axs[1].axvline(0,color="k",lw=.6)
axs[1].set_title("(b) Quality (percentage points)",loc="left"); axs[0].set_xlabel("Difference per +1 SD hardship"); axs[1].set_xlabel("Difference per +1 SD hardship")
fig.legend(handles=[Line2D([],[],marker="o",color="#c0392b",ls="",label="Baseline fixed effects (spec. 4)"),Line2D([],[],marker="s",color="#7f8c8d",ls="",label="+ Ward × year fixed effects (spec. 6)")],loc="lower center",ncol=2,fontsize=7.5,bbox_to_anchor=(0.5,-0.01))
fig.tight_layout(rect=[0,0.05,1,1]); fig.savefig("figs/fig4.png"); plt.close()
# ---------- Fig 5: forest by type
t=pd.DataFrame([{"type":k.split("|",1)[1],**v} for k,v in H.items() if k.startswith("type|")]); t["d"]=t.dept.map(DS); t=t.sort_values("coef")
fig,ax=plt.subplots(figsize=(6.6,8.6)); y=np.arange(len(t))
for yy,(_,rw) in zip(y,t.iterrows()):
    ax.errorbar(pct(rw.coef),yy,xerr=[[pct(rw.coef)-pct(rw.coef-1.96*rw.se)],[pct(rw.coef+1.96*rw.se)-pct(rw.coef)]],fmt="o",ms=3.2,color=DC[rw.d],capsize=1.5,lw=.9)
ax.set_yticks(y); ax.set_yticklabels([s.replace("Request","Req.").replace("Complaint","Compl.") for s in t.type],fontsize=6.8); ax.axvline(0,color="k",lw=.6)
ax.axvline(pct(S["lhrs|(4)"]["coef"]["hs"]),color="#c0392b",ls="--",lw=.8); ax.set_xlabel("% change in completion time per +1 SD hardship (95% CI)")
ax.legend(handles=[Line2D([],[],marker="o",ls="",color=c,label=l) for l,c in DC.items()]+[Line2D([],[],color="#c0392b",ls="--",label="Pooled estimate")],loc="lower right",fontsize=7)
fig.tight_layout(); fig.savefig("figs/fig5.png"); plt.close()
# ---------- Fig 6: year gradient
fig,axs=plt.subplots(1,2,figsize=(7,2.7)); yrs=list(range(2019,2025))
for ax,(k,f,yl) in zip(axs,[("lhrs",pct,"% change in completion time"),("slow",lambda b:100*b,"pp more likely slower than median")]):
    c=H[f"year|{k}"]["coef"]; s=H[f"year|{k}"]["se"]; b=np.array([c[f"hs_{y}"] for y in yrs]); e=np.array([s[f"hs_{y}"] for y in yrs])
    ax.fill_between(yrs,f(b-1.96*e),f(b+1.96*e),color="#c0392b",alpha=.18); ax.plot(yrs,f(b),"o-",color="#c0392b",ms=4)
    ax.axvspan(2019.6,2020.4,color="gray",alpha=.12); ax.text(2020,ax.get_ylim()[1]*0.02,"",fontsize=7); ax.axhline(0,color="k",lw=.6)
    ax.set_ylabel(yl); ax.set_xticks(yrs); ax.set_ylim(bottom=min(0,f(b-1.96*e).min()*1.1))
axs[0].set_title("(a) Completion time",loc="left"); axs[1].set_title("(b) Probability of slower-than-median service",loc="left")
axs[0].text(2020,axs[0].get_ylim()[1]*.92,"COVID-19",ha="center",fontsize=7,color="gray")
fig.tight_layout(); fig.savefig("figs/fig6.png"); plt.close()
# ---------- Fig 7: KM
km=pd.read_csv("tabs/km.csv"); ttl={"Graffiti Removal Request":("(a) Graffiti removal",7),"Street Light Out Complaint":("(b) Street light out",40),"Pothole in Street Complaint":("(c) Pothole in street",40),"Rodent Baiting/Rat Complaint":("(d) Rodent baiting",40)}
fig,axs=plt.subplots(2,2,figsize=(7,5)); axs=axs.ravel()
for ax,(tp,(tt,xm)) in zip(axs,ttl.items()):
    for q in [1,2,3,4]:
        d=km[(km.type==tp)&(km.hq==q)&(km.day<=xm)]; md=A[f"km_med|{tp}|{q}"]
        ax.step(d.day,1-d.S,where="post",color=QC[q-1],lw=1.3,label=f"{QL[q-1].split(' (')[0]} (median {md:.1f} d)")
    ax.set_title(tt,loc="left"); ax.set_xlim(0,xm); ax.set_ylim(0,1); ax.set_xlabel("Days since request"); ax.set_ylabel("Share completed"); ax.legend(fontsize=6.8,loc="lower right")
fig.tight_layout(); fig.savefig("figs/fig7.png"); plt.close()
# ---------- Fig 8: decomposition
D,C=A["decomp"],A["decomp_ci"]
fig,axs=plt.subplots(1,2,figsize=(7.2,2.8),gridspec_kw={"width_ratios":[1.25,1]})
items=[("Total gap\n(Q4 − Q1)",D["total"],C["total"],"#34495e"),("Request-type\nmix",D["comp_type"],C["comp_type"],"#95a5a6"),("Channel\nmix",D["comp_chan_increment"],C["comp_chan_increment"],"#95a5a6"),("Differential\ntreatment",D["within_full"],C["within_full"],"#c0392b")]
for i,(l,v,ci,c) in enumerate(items):
    axs[0].bar(i,v,color=c,width=.6); axs[0].errorbar(i,v,yerr=[[v-ci[0]],[ci[1]-v]],color="k",capsize=3,lw=.9); axs[0].text(i,max(v,ci[1])+.012,f"{v:.3f}",ha="center",fontsize=7.5)
axs[0].set_xticks(range(4)); axs[0].set_xticklabels([x[0] for x in items],fontsize=7.5); axs[0].axhline(0,color="k",lw=.6); axs[0].set_ylabel("Log points (mean log completion time)")
axs[0].set_title("(a) Decomposition of the Q4–Q1 gap",loc="left")
dd=pd.Series(A["decomp_dept"]).rename(index=DS).sort_values()
axs[1].barh(range(len(dd)),dd.values,color=[DC[k] for k in dd.index]); axs[1].set_yticks(range(len(dd))); axs[1].set_yticklabels(dd.index,fontsize=7.5); axs[1].axvline(0,color="k",lw=.6)
axs[1].set_xlabel("Contribution to differential treatment (log points)"); axs[1].set_title("(b) Differential treatment by department",loc="left")
fig.tight_layout(); fig.savefig("figs/fig8.png"); plt.close()
# ---------- Fig 9: channels (separate regressions)
from prep import get; from fe import feols
r=get(["lhrs"]); cs={}
for ch in ["phone","digital","alderman"]:
    m=feols(r[r.chan==ch],"lhrs",["hs","lwl"],fes=["ty","ym","dow","hod"]); cs[ch]={"b":m["coef"]["hs"],"se":m["se"]["hs"],"p":m["p"]["hs"],"n":m["n"],"ymean":m["ymean"]}
json.dump(cs,open("tabs/chan_sep.json","w"),default=float); del r
t3=pd.read_csv("tabs/t3_outcomes_by_q.csv",index_col=0).iloc[:4]
fig,axs=plt.subplots(1,2,figsize=(7.2,2.8))
dig,ald=t3["digital_%"].values,t3["alderman_%"].values; ph=100-dig-ald; x=np.arange(4)
axs[0].bar(x,ph,color="#7f8c8d",label="Phone"); axs[0].bar(x,dig,bottom=ph,color="#2980b9",label="Web / mobile app"); axs[0].bar(x,ald,bottom=ph+dig,color="#f39c12",label="Aldermanic office")
for i in x: axs[0].text(i,ph[i]+dig[i]/2,f"{dig[i]:.0f}%",ha="center",va="center",color="white",fontsize=7.5)
axs[0].set_xticks(x); axs[0].set_xticklabels(["Q1\nlowest","Q2","Q3","Q4\nhighest"]); axs[0].set_ylabel("% of resident requests"); axs[0].set_title("(a) Reporting channel by hardship quartile",loc="left"); axs[0].legend(fontsize=6.8,loc="upper center",bbox_to_anchor=(0.5,-0.24),ncol=3)
labs=[("All channels",S["lhrs|(4)"]["coef"]["hs"],S["lhrs|(4)"]["se"]["hs"])]+[(n,cs[k]["b"],cs[k]["se"]) for n,k in [("Phone","phone"),("Web / mobile app","digital"),("Aldermanic office","alderman")]]
for i,(l,b,se) in enumerate(labs): axs[1].errorbar(pct(b),i,xerr=[[pct(b)-pct(b-1.96*se)],[pct(b+1.96*se)-pct(b)]],fmt="o",color=["#34495e","#7f8c8d","#2980b9","#f39c12"][i],capsize=2.5,ms=4.5)
axs[1].set_yticks(range(4)); axs[1].set_yticklabels([l[0] for l in labs]); axs[1].invert_yaxis(); axs[1].axvline(0,color="k",lw=.6)
axs[1].set_xlabel("% change per +1 SD hardship"); axs[1].set_title("(b) Hardship gradient by channel",loc="left")
fig.tight_layout(); fig.savefig("figs/fig9.png"); plt.close()
# ---------- Fig 10: concentration curves
cc=pd.read_csv("tabs/ca_counts.csv").sort_values("hardship",ascending=False)
fig,ax=plt.subplots(figsize=(4.8,5.6)); P=np.r_[0,np.cumsum(cc["pop"])/cc["pop"].sum()]
for v,l,c in [("violent","Violent crime (need benchmark)","#8e44ad"),("bviol","Recorded building violations (need benchmark)","#16a085"),("slow_n","Slower-than-median requests","#c0392b"),("res","Resident 311 requests","#2c3e50"),("digital","Web / app requests","#2980b9")]:
    ax.plot(P,np.r_[0,np.cumsum(cc[v])/cc[v].sum()],color=c,lw=1.4,label=f"{l}  (CI = {A['ci|'+v][0]:.3f})")
ax.plot([0,1],[0,1],color="k",lw=.7,ls="--",label="Line of equality"); ax.set_xlabel("Cumulative share of population\n(community areas ranked from highest to lowest hardship)"); ax.set_ylabel("Cumulative share of outcome")
ax.legend(fontsize=6.8,loc="upper center",bbox_to_anchor=(0.45,-0.17)); ax.set_xlim(0,1); ax.set_ylim(0,1); fig.tight_layout(); fig.savefig("figs/fig10.png"); plt.close()
# ---------- Fig 11: robustness
rows=[("Type × year FE only","Specification",S["lhrs|(1)"]),("+ month, weekday, hour FE","Specification",S["lhrs|(2)"]),("+ channel FE","Specification",S["lhrs|(3)"]),("+ workload (baseline)","Specification",S["lhrs|(4)"]),
 ("+ density, distance to Loop, population","Controls",S["lhrs|(5)"]),("+ violent crime rate","Controls",R["crime"]),("+ building violation rate","Controls",R["need_bviol"]),("+ ward × year FE","Controls",S["lhrs|(6)"]),
 ("Type × year × channel FE","Specification",R["tyc_fe"]),("Excluding 2020","Sample",R["excl2020"]),("Excluding sub-minute closures","Sample",R["excl_subminute"]),("Excluding downtown areas","Sample",R["excl_downtown"]),
 ("Excluding long-horizon programs","Sample",R["excl_longprog"]),("Unwinsorized durations","Sample",R["unwinsorized"]),("Community areas weighted equally","Inference",R["ca_equal_weight"]),("SEs clustered by ward","Inference",R["cluster_ward"])]
rr=[(l,c,d["coef"]["hs"],d["se"]["hs"]) for l,c,d in rows]
rr+= [("Two-step CA-level OLS (HC3)","Spatial",A["sp|m1"]["hc3_b"],A["sp|m1"]["hc3_se"]),("Spatial lag model (direct coef.)","Spatial",A["sp|m1"]["lag_b"][1],A["sp|m1"]["lag_se"][1]),("Spatial error model","Spatial",A["sp|m1"]["err_b"][1],A["sp|m1"]["err_se"][1])]
rr=sorted(rr,key=lambda x:x[2]); CC={"Specification":"#34495e","Controls":"#d35400","Sample":"#27ae60","Inference":"#8e44ad","Spatial":"#2980b9"}
fig,ax=plt.subplots(figsize=(6.4,5.2))
for i,(l,c,b,se) in enumerate(rr): ax.errorbar(pct(b),i,xerr=[[pct(b)-pct(b-1.96*se)],[pct(b+1.96*se)-pct(b)]],fmt="o",color=CC[c],capsize=2,ms=4)
ax.set_yticks(range(len(rr))); ax.set_yticklabels([x[0] for x in rr],fontsize=7.3); ax.axvline(0,color="k",lw=.6); ax.axvline(pct(S["lhrs|(4)"]["coef"]["hs"]),color="gray",ls="--",lw=.7)
ax.set_xlabel("% change in completion time per +1 SD hardship (95% CI)"); ax.legend(handles=[Line2D([],[],marker="o",ls="",color=v,label=k) for k,v in CC.items()],fontsize=7,loc="lower right")
fig.tight_layout(); fig.savefig("figs/fig11.png"); plt.close()
# contact sheet
from PIL import Image
ims=[Image.open(f"figs/fig{i}.png") for i in [1,3,4,9,10]]; W=700
th=[im.resize((W,int(im.height*W/im.width))) for im in ims]; cols=3; rows_=int(np.ceil(len(th)/cols)); rh=[max(t.height for t in th[i*cols:(i+1)*cols]) for i in range(rows_)]
sheet=Image.new("RGB",(W*cols,sum(rh)),"white"); y=0
for i in range(rows_):
    for j,t in enumerate(th[i*cols:(i+1)*cols]): sheet.paste(t,(j*W,y))
    y+=rh[i]
sheet.save("figs/contact.png"); print("ok", {k:round(v['b'],4) for k,v in cs.items()}, {k:round(v['se'],4) for k,v in cs.items()})
