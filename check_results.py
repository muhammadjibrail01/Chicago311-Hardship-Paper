"""Compare your Paper 1 run with the numbers reported in the paper:  python check_results.py"""
import json, os, glob, pandas as pd
from config import W
here=os.path.dirname(os.path.abspath(__file__)); T=lambda f: json.load(open(W+"tabs/"+f))
C=[("Chicago tracts",lambda: len(pd.read_csv(W+"data/chicago_tracts.csv")),792,0),
 ("Analytic tracts",lambda: int(pd.read_csv(W+"tract.csv").analytic.sum()),789,0),
 ("Speed-sample requests in analytic tracts",lambda: T("main_models.json")["S1 hardship"]["n"],3534224,0),
 ("Correlation: tract hardship and Black share (Table 3)",lambda: T("collinearity.json")["corr_tract_hardship_black"],0.478,0.0006),
 ("Hardship only (Table 4, col 1)",lambda: T("main_models.json")["S1 hardship"]["coef"]["z_hardship"],0.076,0.0006),
 ("Hardship with race (col 3)",lambda: T("main_models.json")["S3 both"]["coef"]["z_hardship"],0.004,0.0006),
 ("Black share with hardship (col 3)",lambda: T("main_models.json")["S3 both"]["coef"]["z_pct_black"],0.131,0.0006),
 ("Hispanic share with hardship (col 3)",lambda: T("main_models.json")["S3 both"]["coef"]["z_pct_hisp"],0.049,0.0006),
 ("Black share within community areas (col 4)",lambda: T("main_models.json")["S4 both+CA FE"]["coef"]["z_pct_black"],0.091,0.0006),
 ("Black share with controls (col 5)",lambda: T("main_models.json")["S5 +controls"]["coef"]["z_pct_black"],0.082,0.0006),
 ("Black share with poverty and income (col 6)",lambda: T("main_models.json")["S6 poverty,income+race"]["coef"]["z_pct_black"],0.138,0.0006),
 ("Cell: >60% Black, low poverty (Table 5)",lambda: T("main_models.json")["S7 race-class cells"]["coef"][">60% Black | low poverty"],0.191,0.0006),
 ("Cell: <10% Black, high poverty (Table 5)",lambda: T("main_models.json")["S7 race-class cells"]["coef"]["<10% Black | high poverty"],0.044,0.0006),
 ("Cell within areas: >60% Black, low poverty",lambda: T("main_models.json")["S8 cells+CA FE"]["coef"][">60% Black | low poverty"],0.128,0.0006),
 ("Fixed-scope jobs, citywide (Table 6)",lambda: T("jobscope_channel.json")["scope|fixed"]["coef"]["z_pct_black"],0.063,0.0006),
 ("Fixed-scope jobs, within areas",lambda: T("jobscope_channel.json")["scope|fixed +CA"]["coef"]["z_pct_black"],0.019,0.0006),
 ("Variable-scope jobs, citywide",lambda: T("jobscope_channel.json")["scope|variable"]["coef"]["z_pct_black"],0.312,0.0006),
 ("Streetlight outages",lambda: T("jobscope_channel.json")["type|Street Light Out Complaint"]["coef"]["z_pct_black"],0.097,0.0006),
 ("HOLC grade A vs C (Table 7)",lambda: T("redlining.json")["grade only"]["coef"]["grade_A"],-0.109,0.0006),
 ("Redlining indicator with current composition",lambda: T("redlining.json")["hri+race+hardship"]["coef"]["z_hri"],0.001,0.0006),
 ("C|D border jump, 100 m",lambda: T("redlining.json")["RD CD bw100"]["b"],0.057,0.0006),
 ("B|C border jump, 400 m",lambda: T("redlining.json")["RD BC bw400"]["b"],-0.019,0.0006),
 ("Re-report within 30 days, Black share (Table 8)",lambda: T("quality.json")["recur30"]["coef"]["z_pct_black"],-0.148,0.0006),
 ("Cancellation, Black share",lambda: T("quality.json")["canceled"]["coef"]["z_pct_black"],-0.235,0.0006),
 ("Aldermanic-office requests, Black share",lambda: T("jobscope_channel.json")["chan|alderman"]["coef"]["z_pct_black"],0.028,0.0006),
 ("Ward x year fixed effects (Table 9)",lambda: T("robustness.json")["ward x year FE"]["coef"]["z_pct_black"],0.048,0.0006),
 ("Excluding 2020",lambda: T("robustness.json")["exclude 2020"]["coef"]["z_pct_black"],0.143,0.0006),
 ("Spatial error model, Black share",lambda: T("spatial.json")["ml_error"]["coef"]["z_pct_black"],0.055,0.0006),
 ("Moran's I, adjusted index",lambda: T("spatial.json")["moran|adj"]["I"],0.737,0.0006)]
res={"PASS":0,"DIFF":0,"MISSING":0}
for name,get,exp,tol in C:
    try:
        v=get(); tag="PASS" if abs(v-exp)<=tol+1e-12 else "DIFF"; print(f"[{tag:4}] {name:52s} yours={v:>12,.4f}  paper={exp:>10,.4f}")
    except (FileNotFoundError,KeyError) as e: tag="MISSING"; print(f"[MISS] {name:52s} (not produced yet: {e})")
    res[tag]+=1
print(f"\nFigures produced: {len(glob.glob(W+'figs/fig*.png'))} (paper uses 7) | PASS {res['PASS']} DIFF {res['DIFF']} MISSING {res['MISSING']}")
if os.path.exists(W+"tables_p1.json"):
    old=json.load(open(os.path.join(here,"expected","tables_in_paper.json"))); new=json.load(open(W+"tables_p1.json")); tot=same=0; diffs=[]
    for k in old:
        for i,(a,b) in enumerate(zip(old[k]["rows"],new.get(k,{}).get("rows",[]))):
            for j,(x,y) in enumerate(zip(a,b)):
                tot+=1; same+=(x==y)
                if x!=y: diffs.append(f"{k} row {i} col {j}: paper={x!r} yours={y!r}")
    print(f"Table cells identical to the paper: {same:,} of {tot:,}"); [print("   ",d) for d in diffs[:15]]
