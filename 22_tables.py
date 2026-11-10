import json, numpy as np, pandas as pd
J=lambda f: json.load(open(f"tabs/{f}.json"))
S,Q,H,R,A,CS=J("reg_speed"),J("reg_quality"),J("reg_het"),J("reg_rob"),J("an2"),J("chan_sep")
st=lambda p:"***" if p<.01 else "**" if p<.05 else "*" if p<.1 else ""
def cf(d,v="hs",k=3,m=1): return f"{m*d['coef'][v]:.{k}f}{st(d['p'][v])}"
def se(d,v="hs",k=3,m=1): return f"({m*d['se'][v]:.{k}f})"
N=lambda x:f"{int(x):,}"
T={}
NOTE_FE="Standard errors clustered by community area (77 clusters) in parentheses. *** p<0.01, ** p<0.05, * p<0.1 (t-distribution with G−1 degrees of freedom)."
# T1
T["T1"]={"cap":"Table 1. Sample construction","cols":["Step","Records","Notes"],"widths":[4300,1500,3560],"rows":[
 ["311 service requests created 2019–2024","11,111,549","Three extracts; no overlapping request IDs"],
 ["Excluding information-only calls and aircraft noise complaints","5,226,161","Calls closed on answer; O’Hare noise complaints"],
 ["With a valid community area (1–77)","5,210,130",""],
 ["Core physical-service request types","4,648,843","49 types in five operating departments (Appendix Table A1)"],
 ["Resident-initiated requests","4,240,824","Excludes 408,019 city-generated records (e.g., crew “mass entry”)"],
 ["Resident-initiated, non-duplicate (quality sample)","3,677,012","Used for cancellation, unresolved, administrative closure"],
 ["Completed, non-duplicate, resident-initiated (speed sample)","3,540,652","Used for completion-time models"],
 ["Recurrence sample (30-day window)","3,377,469","Closed by 1 Dec 2024; placeholder addresses removed"],
 [{"panel":"Auxiliary data (community-area level)"}],
 ["Unique crime incidents, 2019–2024","1,447,790","Four overlapping extracts deduplicated on incident ID"],
 ["Building violations geocoded to community areas","343,084","Two extracts, 2019–2024; point-in-polygon join"],
 ["Community areas with census, ACS, and boundary data","77","Hardship Index 2008–2012; ACS 5-year 2019–2023"]],
 "note":"Source: City of Chicago Data Portal extracts downloaded September 2026; author’s calculations."}
# T2
t2=pd.read_csv("tabs/t2_ca_by_q.csv",index_col=0)
lab=[("n_ca","Community areas (n)",0),("hardship","Hardship Index (1–98)",1),("pci","Per capita income ($)",0),("poverty","Households below poverty (%)",1),("unemp","Unemployed, age 16+ (%)",1),("nohs","No high school diploma, age 25+ (%)",1),
 ("lowinc","Household income < $25,000, ACS 2019–23 (%)",1),("pct_black","Black residents (%)",1),("pct_hisp","Hispanic or Latino residents (%)",1),("pct_nhwhite","Non-Hispanic White residents (%)",1),
 ("pop","Population (total)",0),("density","Population density (per km²)",0),("viol_rate","Violent crimes per 1,000 per year",1),("bviol_rate","Building violations per 1,000 per year",1),("dist","Distance to the Loop (km)",1)]
rows=[[l]+[(f"{t2.loc[q,k]:,.{d}f}") for q in ["1","2","3","4","All"]] for k,l,d in lab]
T["T2"]={"cap":"Table 2. Community-area characteristics by hardship quartile","cols":["","Q1 (lowest)","Q2","Q3","Q4 (highest)","All"],"widths":[3560,1160,1160,1160,1160,1160],"rows":rows,
 "note":"Unweighted means across community areas, except population (sum). Quartiles are defined over the 77 community areas using the 2008–2012 Hardship Index. Crime and building-violation rates use ACS 2019–2023 population and 2019–2024 counts."}
# T3
t3=pd.read_csv("tabs/t3_outcomes_by_q.csv",index_col=0)
lab=[("resident_requests","Resident-initiated requests",0),("req_per_1000_yr","Requests per 1,000 residents per year",1),("city_generated_%","City-generated share of all records (%)",1),("digital_%","Web / mobile-app share (%)",1),("alderman_%","Aldermanic-office share (%)",1),
 ("median_hours","Median completion time (hours)",1),("mean_log_hours","Mean log(1 + hours)",3),("slower_than_type_median_%","Slower than type–year median (%)",1),("canceled_%","Canceled (%)",2),("unresolved_%","Still open at extraction (%)",2),
 ("admin_close_%","Closed within one minute (%)",2),("duplicate_%","Flagged duplicate (%)",1),("recur30_%","Re-reported within 30 days of closure (%)",1),("recur90_%","Re-reported within 90 days of closure (%)",1)]
rows=[[l]+[f"{t3.loc[q,k]:,.{d}f}" for q in ["1","2","3","4","All"]] for k,l,d in lab]
T["T3"]={"cap":"Table 3. Unadjusted service outcomes by hardship quartile","cols":["","Q1 (lowest)","Q2","Q3","Q4 (highest)","All"],"widths":[3560,1160,1160,1160,1160,1160],"rows":rows,
 "note":"Request-level means within quartiles. Speed and recurrence measures use the speed sample; cancellation, unresolved, and administrative-closure measures use resident-initiated non-duplicate requests. Unadjusted differences partly reflect request mix; see Tables 4–5."}
# T4
def panel(y,lab,k,m=1):
    out=[[{"panel":lab}]]
    out.append(["Hardship Index (SD)"]+[cf(S[f"{y}|({i})"],"hs",k,m) for i in range(1,7)])
    out.append([""]+[se(S[f"{y}|({i})"],"hs",k,m) for i in range(1,7)])
    out.append(["log(workload)"]+["","",""]+[cf(S[f"{y}|({i})"],"lwl",k,m) for i in range(4,7)])
    out.append([""]+["","",""]+[se(S[f"{y}|({i})"],"lwl",k,m) for i in range(4,7)])
    out.append(["Mean of dependent variable"]+[f"{m*S[f'{y}|({i})']['ymean']:.{2 if y!='lhrs' else 3}f}" for i in range(1,7)])
    out.append(["Within R²"]+[f"{S[f'{y}|({i})']['r2w']:.4f}" for i in range(1,7)])
    return out
ck="✓"
rows=panel("lhrs","Panel A. log(1 + hours to completion)",3)+panel("prank","Panel B. Within type–year percentile rank of completion time (0–100)",2)+panel("slow","Panel C. Slower than type–year median (percentage points)",2,100)
rows+=[[{"panel":"Fixed effects and controls"}],["Request type × year FE"]+[ck]*6,["Month-of-sample, weekday, hour FE",""]+[ck]*5,["Reporting-channel FE","",""]+[ck]*4,["Geographic controls","","","","",ck,""],["Ward × year FE","","","","","",ck],
 ["Observations"]+[N(S["lhrs|(1)"]["n"])]*6,["Community-area clusters"]+["77"]*6]
T["T4"]={"cap":"Table 4. Neighborhood hardship and the speed of 311 service completion","cols":["","(1)","(2)","(3)","(4)","(5)","(6)"],"widths":[3060,1050,1050,1050,1050,1050,1050],"rows":rows,"font":8,
 "note":"Speed sample of completed, non-duplicate, resident-initiated requests. The Hardship Index is standardized across community areas (1 SD = 28.7 index points). Workload is the number of resident requests of the same type in the same community area and week. Geographic controls are log population density, distance to the Loop, and log population. Completion times are winsorized at the type-specific 99th percentile. "+NOTE_FE}
# T5
qo=[("canceled","Canceled"),("unresolved","Unresolved"),("adminclose","Closed < 1 min"),("dup","Duplicate"),("recur30","Re-reported ≤ 30 d"),("recur90","Re-reported ≤ 90 d")]
rows=[]
for s,lab in [("main","Panel A. Baseline fixed effects (specification 4)"),("ward","Panel B. Adding ward × year fixed effects (specification 6)")]:
    rows+=[[{"panel":lab}],["Hardship Index (SD)"]+[cf(Q[f"{k}|{s}"],"hs",3) for k,_ in qo],[""]+[se(Q[f"{k}|{s}"],"hs",3) for k,_ in qo]]
rows+=[["Mean of dependent variable (%)"]+[f"{Q[k+'|main']['ymean']:.2f}" for k,_ in qo],["Observations"]+[N(Q[k+'|main']['n']) for k,_ in qo],["Sample"]+["Quality"]*3+["Resident"]+["Speed"]*2]
T["T5"]={"cap":"Table 5. Neighborhood hardship and the quality of 311 service resolution","cols":[""]+[l for _,l in qo],"widths":[2560,1130,1130,1130,1130,1140,1140],"rows":rows,"font":8,
 "note":"Linear probability models; outcomes scaled 0–100 so coefficients are percentage points. All models include request type × year, month-of-sample, weekday, hour, and channel fixed effects and log workload. “Quality” = resident-initiated non-duplicate requests; “Resident” = all resident-initiated requests; “Speed” = completed non-duplicate resident requests with a full post-closure window. "+NOTE_FE}
# T6
DS={"Streets and Sanitation":"Streets & Sanitation","CDOT - Department of Transportation":"Transportation (CDOT)","DWM - Department of Water Management":"Water Management (DWM)","Animal Care and Control":"Animal Care & Control","DOB - Buildings":"Buildings (DOB)"}
def c1(d,k=3,m=1): return f"{m*d['coef']:.{k}f}{st(d['p'])}", f"({m*d['se']:.{k}f})"
rows=[[{"panel":"Panel A. By operating department"}]]
for dk,dl in DS.items():
    a,b=c1(H[f"dept|{dk}|lhrs"]); c,d=c1(H[f"dept|{dk}|slow"],2,100); rows.append([dl,a,b,c,d,N(H[f"dept|{dk}|lhrs"]["n"])])
rows.append([{"panel":"Panel B. By reporting channel (separate regressions)"}])
for k,l in [("phone","Phone"),("digital","Web / mobile app"),("alderman","Aldermanic office")]:
    d=CS[k]; rows.append([l,f"{d['b']:.3f}{st(d['p'])}",f"({d['se']:.3f})","—","—",N(d["n"])])
rows.append([{"panel":"Panel C. By year (interacted model)"}])
for y in range(2019,2025):
    a=H["year|lhrs"]; b=H["year|slow"]; k=f"hs_{y}"
    rows.append([str(y),f"{a['coef'][k]:.3f}{st(a['p'][k])}",f"({a['se'][k]:.3f})",f"{100*b['coef'][k]:.2f}{st(b['p'][k])}",f"({100*b['se'][k]:.2f})",""])
T["T6"]={"cap":"Table 6. Heterogeneity in the hardship gradient in completion time","cols":["","log(1+hours) β","SE","Slower than median (pp) β","SE","Observations"],"widths":[2860,1300,1000,1600,1000,1600],"rows":rows,"font":8,
 "note":"Each row in Panels A and B is a separate regression of the indicated outcome on the standardized Hardship Index with the baseline fixed effects (specification 4); channel fixed effects are omitted in Panel B. Panel C interacts hardship with year indicators in the pooled speed sample (N = 3,540,652). "+NOTE_FE}
# T7
cols7=[("baseline",["hs"]),("race",["hs","z_pct_black","z_pct_hisp"]),("race_only",["z_pct_black","z_pct_hisp"]),("lowinc_acs",["z_lowinc"]),("hs+lowinc",["hs","z_lowinc"]),("crime",["hs","z_viol_rate"]),("need_bviol",["hs","z_bviol_rate"])]
vl=[("hs","Hardship Index, 2008–12"),("z_pct_black","Black residents (%)"),("z_pct_hisp","Hispanic residents (%)"),("z_lowinc","Low-income households, ACS 2019–23 (%)"),("z_viol_rate","Violent crime rate"),("z_bviol_rate","Building violation rate")]
rows=[]
for v,l in vl:
    rows.append([l]+[cf(R[k],v) if v in X else "" for k,X in cols7]); rows.append([""]+[se(R[k],v) if v in X else "" for k,X in cols7])
rows.append(["Observations"]+[N(R[k]["n"]) for k,_ in cols7])
T["T7"]={"cap":"Table 7. Class, race, and need: competing community-area measures","cols":["","(1)","(2)","(3)","(4)","(5)","(6)","(7)"],"widths":[2960,915,915,915,915,915,915,910],"rows":rows,"font":8,
 "note":"Dependent variable: log(1 + hours to completion). All community-area measures are standardized (mean 0, SD 1 across the 77 areas). All models include the baseline fixed effects and log workload (specification 4). Correlations across community areas: hardship–% Black 0.47; low income–% Black 0.74; hardship–low income 0.74. "+NOTE_FE}
# T8
comp=[("comp_poverty","Households below poverty"),("comp_unemp","Unemployment, age 16+"),("comp_nohs","No high school diploma, age 25+"),("comp_crowded","Crowded housing"),("comp_dependency","Dependency (age < 18 or > 64)"),("comp_lpci","log per capita income"),("lowinc_acs","Low-income households, ACS 2019–23")]
rows=[]
for k,l in comp:
    v=[x for x in R[k]["coef"] if x!="lwl"][0]; rows.append([l,f"{R[k]['coef'][v]:.3f}{st(R[k]['p'][v])}",f"({R[k]['se'][v]:.3f})",f"{100*(np.exp(R[k]['coef'][v])-1):.1f}%"])
T["T8"]={"cap":"Table 8. Components of hardship entered one at a time","cols":["Standardized measure","β","SE","Implied change in completion time"],"widths":[4160,1600,1600,2000],"rows":rows,
 "note":"Each row is a separate regression of log(1 + hours) on one standardized community-area measure with the baseline fixed effects and log workload (N = 3,540,652). "+NOTE_FE}
# T9
D,C,DD=A["decomp"],A["decomp_ci"],A["decomp_dept"]; tot=D["total"]
def rw(l,v,ci=None): return [l,f"{v:.3f}",f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "",f"{100*v/tot:.1f}"]
rows=[rw("Raw gap in mean log(1 + hours), Q4 − Q1",tot,C["total"]),[{"panel":"Explained by composition"}],rw("Request type × year mix",D["comp_type"],C["comp_type"]),rw("Reporting-channel mix (incremental)",D["comp_chan_increment"],C["comp_chan_increment"]),
 rw("Total composition (type × year × channel)",D["comp_full"],C["comp_full"]),[{"panel":"Unexplained: differential treatment within cells"}],rw("Within-cell difference",D["within_full"],C["within_full"])]
for dk,dl in DS.items(): rows.append(rw("   of which "+dl,DD[dk]))
T["T9"]={"cap":"Table 9. Decomposition of the Q4–Q1 gap in completion time","cols":["Component","Log points","95% CI","% of gap"],"widths":[4760,1400,1800,1400],"rows":rows,
 "note":"Nonparametric (cell-based) Oaxaca–Blinder decomposition using 882 request type × year × channel cells, with Q1 cell means as the reference structure; all cells have common support. Confidence intervals from 500 bootstrap replications that resample community areas within quartiles."}
# T10
def hr(d,v): x=d[v]; return f"{x['hr']:.3f}{st(x['p'])}", f"[{x['lo']:.3f}, {x['hi']:.3f}]"
m1,m2=A["cox_hs"],A["cox_q"]; rows=[]
for v,l in [("hs","Hardship Index (SD)"),("q2","Hardship quartile 2"),("q3","Hardship quartile 3"),("q4","Hardship quartile 4 (highest)"),("c_digital","Web / mobile app (vs. phone)"),("c_alderman","Aldermanic office (vs. phone)"),("lwl","log(workload)")]:
    a=hr(m1,v) if v in m1 else ("",""); b=hr(m2,v) if v in m2 else ("","")
    rows.append([l,a[0],a[1],b[0],b[1]])
rows+=[["Year indicators","Yes","","Yes",""],["Baseline hazard stratified by request type","Yes","","Yes",""],["Requests (random sample)",N(m1["n"]),"",N(m2["n"]),""],["Completions (events)",N(m1["events"]),"",N(m2["events"]),""]]
T["T10"]={"cap":"Table 10. Cox proportional-hazards models of time to completion","cols":["","Model 1: HR","95% CI","Model 2: HR","95% CI"],"widths":[3560,1250,1650,1250,1650],"rows":rows,
 "note":f"Hazard ratios below 1 indicate slower completion. Random sample of 120,000 resident-initiated non-duplicate requests (from {A['surv_n']:,}); canceled and still-open requests are right-censored at cancellation or at the extraction date (23 September 2026). Robust standard errors clustered by community area. *** p<0.01, ** p<0.05, * p<0.1."}
# T11
s1,s2=A["sp|m1"],A["sp|m2"]
f3=lambda b,s:(f"{b:.3f}",f"({s:.3f})")
rows=[["Hardship Index (SD)",f"{s1['hc3_b']:.3f}{st(s1['hc3_p'])}",f"{s1['lag_b'][1]:.3f}",f"{s1['err_b'][1]:.3f}",f"{s2['hc3_b']:.3f}{st(s2['hc3_p'])}",f"{s2['lag_b'][1]:.3f}",f"{s2['err_b'][1]:.3f}"],
 ["",f"({s1['hc3_se']:.3f})",f"({s1['lag_se'][1]:.3f})",f"({s1['err_se'][1]:.3f})",f"({s2['hc3_se']:.3f})",f"({s2['lag_se'][1]:.3f})",f"({s2['err_se'][1]:.3f})"],
 ["Black residents (%, SD)","","","",f"{s2['zblack_b']:.3f}{st(s2['zblack_p'])}",f"{s2['lag_b'][2]:.3f}",f"{s2['err_b'][2]:.3f}"],["","","","",f"({s2['zblack_se']:.3f})",f"({s2['lag_se'][2]:.3f})",f"({s2['err_se'][2]:.3f})"],
 ["Spatial autoregressive parameter (ρ or λ)","",f"{s1['lag_b'][-1]:.3f}",f"{s1['err_b'][-1]:.3f}","",f"{s2['lag_b'][-1]:.3f}",f"{s2['err_b'][-1]:.3f}"],["","",f"({s1['lag_se'][-1]:.3f})",f"({s1['err_se'][-1]:.3f})","",f"({s2['lag_se'][-1]:.3f})",f"({s2['err_se'][-1]:.3f})"],
 ["Wild bootstrap p-value (hardship)",f"{s1['wild_p']:.4f}","","",f"{s2['wild_p']:.4f}","",""],["R²",f"{s1['r2']:.3f}","","",f"{s2['r2']:.3f}","",""],
 ["AIC",f"{s1['ols_aic']:.1f}",f"{s1['lag_aic']:.1f}",f"{s1['err_aic']:.1f}",f"{s2['ols_aic']:.1f}",f"{s2['lag_aic']:.1f}",f"{s2['err_aic']:.1f}"],
 ["Moran’s I of OLS residuals",f"{s1['moran_res'][0]:.3f}***","","",f"{s2['moran_res'][0]:.3f}***","",""],
 ["LM-lag / robust LM-lag",f"{s1['lm_lag'][0]:.1f} / {s1['rlm_lag'][0]:.1f}","","",f"{s2['lm_lag'][0]:.1f} / {s2['rlm_lag'][0]:.1f}","",""],
 ["LM-error / robust LM-error",f"{s1['lm_err'][0]:.1f} / {s1['rlm_err'][0]:.1f}","","",f"{s2['lm_err'][0]:.1f} / {s2['rlm_err'][0]:.2f}","",""]]
T["T11"]={"cap":"Table 11. Community-area models with spatial dependence","cols":["","OLS","Spatial lag","Spatial error","OLS","Spatial lag","Spatial error"],"widths":[2960,1070,1070,1070,1070,1070,1050],"rows":rows,"font":8,
 "note":"N = 77 community areas. Dependent variable: type-adjusted completion-time index (mean community-area residual, in log points, from the baseline model without hardship). Queen-contiguity weights, row-standardized. OLS standard errors are HC3; wild bootstrap uses 9,999 Rademacher draws with the null imposed. Spatial models estimated by maximum likelihood. LM statistics are distributed χ²(1); critical value at p = 0.05 is 3.84."}
# T12
ci=[("res","Resident 311 requests"),("phone","Phone requests"),("digital","Web / mobile-app requests"),("city","City-generated (proactive) records"),("slow_n","Slower-than-median requests (delay burden)"),("bldg311","Building-related 311 complaints"),("bviol","Recorded building violations (need)"),("violent","Violent crime incidents (need)")]
rows=[[l,f"{A['ci|'+k][0]:.3f}",f"[{A['ci|'+k][1]:.3f}, {A['ci|'+k][2]:.3f}]"] for k,l in ci]
T["T12"]={"cap":"Table 12. Concentration indices of service activity and need across community areas","cols":["Per-capita indicator","Concentration index","95% CI"],"widths":[5160,2000,2200],"rows":rows,
 "note":"Population-weighted concentration indices with community areas ranked from highest to lowest hardship; negative values indicate concentration in high-hardship areas, and 0 indicates proportionality to population. Confidence intervals from 2,000 bootstrap replications resampling community areas."}
# T13
rows=[]
for v,l in [("z_hardship","Hardship Index (SD)"),("z_bviol_rate","Building violation rate (SD)"),("z_viol_rate","Violent crime rate (SD)"),("z_pct_black","Black residents (%, SD)")]:
    r_=[l]; r2=[""]
    for m in ["p1","p2","p3"]:
        d=A["pois|"+m]
        if v in d: r_.append(f"{d[v]['irr']:.3f}{st(d[v]['p'])}"); r2.append(f"[{d[v]['lo']:.3f}, {d[v]['hi']:.3f}]")
        else: r_.append(""); r2.append("")
    rows+= [r_,r2]
rows+=[["Request type × year FE","Yes","Yes","Yes"],["Offset: log population","Yes","Yes","Yes"],["Community area × type × year cells",N(A["pois|p1"]["n"]),N(A["pois|p2"]["n"]),N(A["pois|p3"]["n"])]]
T["T13"]={"cap":"Table 13. Reporting intensity relative to need: Poisson models of resident requests","cols":["","(1)","(2)","(3)"],"widths":[3960,1800,1800,1800],"rows":rows,
 "note":"Incidence rate ratios with 95% confidence intervals; dependent variable is the count of resident-initiated non-duplicate requests in each community area × request type × year cell (including zeros). Standard errors clustered by community area. *** p<0.01, ** p<0.05, * p<0.1."}
# A1
tp=pd.read_csv("tabs/type_profile.csv").set_index("type")
ty=[(k.split("|",1)[1],v) for k,v in H.items() if k.startswith("type|")]
ty=sorted(ty,key=lambda x:(x[1]["dept"],-tp.loc[x[0],"n"]))
rows=[[t,DS[v["dept"]],N(tp.loc[t,"n"]),N(v["n"]),f"{v['med_hrs']:.0f}",f"{100*(np.exp(v['coef'])-1):.1f}{st(v['p'])}",f"({100*v['se']:.1f})"] for t,v in ty]
T["A1"]={"cap":"Table A1. Core request types: volume, typical completion time, and type-specific hardship gradient","cols":["Request type","Department","All records","Speed sample","Median hours","% per SD","SE"],"widths":[3000,1700,1000,1000,850,950,860],"rows":rows,"font":7,
 "note":"“All records” counts all 2019–2024 requests of the type with a valid community area; “speed sample” counts completed non-duplicate resident requests. Median hours from the speed sample. The gradient is 100 × [exp(β) − 1] from a within-type regression of log(1 + hours) on standardized hardship with month-of-sample, weekday, hour, and channel fixed effects and log workload; SE in percentage points (approximate). Clustered by community area."}
# A2
T["A2"]={"cap":"Table A2. Variable definitions","cols":["Variable","Definition"],"widths":[2400,6960],"rows":[
 ["Completion time","Hours from request creation to closure for completed requests; winsorized at the type-specific 99th percentile; modeled as log(1 + hours)."],
 ["Percentile rank","Within request type × year percentile (0–100) of completion time among speed-sample requests."],
 ["Slower than median","Indicator that completion time exceeds the request type × year median."],
 ["Canceled; Unresolved","Status “Canceled”; status “Open” as of the 23 September 2026 extraction (≥ 21 months after creation)."],
 ["Closed within one minute","Closure time ≤ 1 minute after creation: administrative closure without field work."],
 ["Duplicate","City flag that the request duplicates an open request for the same problem."],
 ["Re-reported within 30/90 days","Another resident request of the same type at the same address created within 30 (90) days after the focal request was closed as completed."],
 ["Hardship Index","Composite of crowded housing, poverty, unemployment, education, dependency, and per capita income (City of Chicago, 2008–2012 ACS); standardized across community areas."],
 ["Reporting channel","Phone (phone, walk-in, mail, fax); web / mobile app (web portal, CHI311 app, Open311 clients, e-mail); aldermanic office; city-generated (mass entry, in-house, department systems)."],
 ["Workload","Number of resident non-duplicate requests of the same type in the same community area and calendar week (log)."],
 ["Adjusted completion-time index","Community-area mean residual (log points) from the baseline model excluding hardship; used in maps and spatial models."],
 ["Need benchmarks","Violent Index crimes (FBI codes 01A, 02, 03, 04A, 04B) and recorded building violations per 1,000 residents per year, 2019–2024."]],"font":8,"note":""}
# A3
g=pd.read_csv("tabs/ca_spatial.csv").sort_values("ca")
rows=[[str(int(r.ca)),r["name"].title().replace("'S","’s").replace("Ohare","O’Hare"),f"{r.hardship:.0f}",str(int(r.hq)),f"{r.req_pc:.0f}",f"{100*(np.exp(r.adj_lhrs)-1):+.1f}",f"{100*r.digital_share:.0f}",r.lisa if r.lisa!="ns" else "—"] for _,r in g.iterrows()]
T["A3"]={"cap":"Table A3. Community-area service profile","cols":["#","Community area","Hardship","Quartile","Requests per 1,000/yr","Adjusted time (%)","Web/app (%)","LISA cluster"],"widths":[450,2500,950,850,1250,1200,1050,1110],"rows":rows,"font":7,
 "note":"Adjusted time is 100 × [exp(index) − 1], where the index is the community-area mean residual from the baseline completion-time model without hardship; positive values indicate slower-than-average service for the same request type, year, month, weekday, hour, and channel. LISA clusters significant at p < 0.05 (9,999 permutations)."}
json.dump(T,open("tables.json","w"),ensure_ascii=False)
print({k:len(v["rows"]) for k,v in T.items()})
print(T["T9"]["rows"][:7]); print(T["T4"]["rows"][1:3])
