"""Compare your run with the numbers reported in the paper.   python check_results.py
PASS = matches the paper (within rounding); DIFF = differs; MISSING = that step has not run yet."""
import json, os, math, glob
import pyarrow.parquet as pq
from config import WORK_DIR
T = lambda f: json.load(open(os.path.join(WORK_DIR, "tabs", f)))
rows = lambda f: pq.ParquetFile(os.path.join(WORK_DIR, f)).metadata.num_rows
C = [  # (what the paper reports, how to read it from your run, expected value, tolerance)
 ("Raw 311 requests",                          lambda: T("raw_audit.json")["rows"],                         11111549, 0),
 ("Unique request IDs",                        lambda: T("raw_audit.json")["unique_ids"],                   11111549, 0),
 ("Analysis records (Table 1)",                lambda: rows("req.parquet"),                                  5210130, 0),
 ("Core-type requests (Table 1)",              lambda: rows("core.parquet"),                                 4648843, 0),
 ("Speed sample N (Table 4)",                  lambda: T("reg_speed.json")["lhrs|(4)"]["n"],                 3540652, 0),
 ("Hardship: main estimate, log hours (T4 c4)",lambda: T("reg_speed.json")["lhrs|(4)"]["coef"]["hs"],       0.0807, 0.0006),
 ("  its clustered SE",                        lambda: T("reg_speed.json")["lhrs|(4)"]["se"]["hs"],         0.0123, 0.0006),
 ("  as % longer per SD (abstract: 8.4%)",     lambda: 100*(math.exp(T("reg_speed.json")["lhrs|(4)"]["coef"]["hs"])-1), 8.4, 0.06),
 ("Type x year FE only (T4 c1)",               lambda: T("reg_speed.json")["lhrs|(1)"]["coef"]["hs"],       0.062, 0.0006),
 ("Within wards (T4 c6)",                      lambda: T("reg_speed.json")["lhrs|(6)"]["coef"]["hs"],       0.022, 0.0006),
 ("Top vs bottom quartile (abstract: ~20%)",   lambda: T("reg_speed.json")["lhrs|quart"]["coef"]["q4"],     0.185, 0.0006),
 ("Percentile rank (T4 panel B)",              lambda: T("reg_speed.json")["prank|(4)"]["coef"]["hs"],      1.15, 0.006),
 ("Slower than median, pp (T4 panel C)",       lambda: 100*T("reg_speed.json")["slow|(4)"]["coef"]["hs"],   1.64, 0.006),
 ("Cancellation, pp (Table 5)",                lambda: T("reg_quality.json")["canceled|main"]["coef"]["hs"], -0.163, 0.0006),
 ("30-day re-report, pp (Table 5)",            lambda: T("reg_quality.json")["recur30|main"]["coef"]["hs"],  -0.018, 0.0006),
 ("Streets & Sanitation gradient (Table 6)",   lambda: T("reg_het.json")["dept|Streets and Sanitation|lhrs"]["coef"], 0.082, 0.0006),
 ("Buildings gradient (Table 6)",              lambda: T("reg_het.json")["dept|DOB - Buildings|lhrs"]["coef"], -0.004, 0.0006),
 ("Gradient in 2019 (Figure 6)",               lambda: T("reg_het.json")["year|lhrs"]["coef"]["hs_2019"],   0.039, 0.0006),
 ("Gradient in 2022 (Figure 6)",               lambda: T("reg_het.json")["year|lhrs"]["coef"]["hs_2022"],   0.113, 0.0006),
 ("Hardship with race controls (Table 7)",     lambda: T("reg_rob.json")["race"]["coef"]["hs"],             0.021, 0.0006),
 ("Share Black residents (Table 7)",           lambda: T("reg_rob.json")["race"]["coef"]["z_pct_black"],    0.116, 0.0006),
 ("Low-income share, ACS (Table 7)",           lambda: T("reg_rob.json")["lowinc_acs"]["coef"]["z_lowinc"], 0.118, 0.0006),
 ("Decomposition: total gap (Table 9)",        lambda: T("an2.json")["decomp"]["total"],                     0.216, 0.0006),
 ("  share within identical cells (88%)",      lambda: T("an2.json")["decomp"]["within_full"]/T("an2.json")["decomp"]["total"], 0.88, 0.006),
 ("Cox hazard ratio per SD (Table 10)",        lambda: T("an2.json")["cox_hs"]["hs"]["hr"],                  0.969, 0.0006),
 ("Moran's I, adjusted index (Section 6.9)",   lambda: T("an2.json")["moran|adj_lhrs"]["I"],                 0.45, 0.006),
 ("CA-level estimate, HC3 (Table 11)",         lambda: T("an2.json")["sp|m1"]["hc3_b"],                      0.066, 0.0006),
 ("Concentration index, requests (Table 12)",  lambda: T("an2.json")["ci|res"][0],                           -0.088, 0.0006),
 ("Poisson IRR per SD (Table 13)",             lambda: T("an2.json")["pois|p1"]["z_hardship"]["irr"],        1.156, 0.0006),
 ("Within-ward share of hardship variance",    lambda: T("audit_models.json")["within_ward_share_hs_var"],  0.30, 0.006),
 ("Leave-one-out minimum",                     lambda: T("audit_models.json")["loo_min"],                    0.077, 0.0006),
 ("Leave-one-out maximum",                     lambda: T("audit_models.json")["loo_max"],                    0.085, 0.0006),
 ("Ambiguous origins as resident",             lambda: T("audit_models.json")["amb_as_resident"]["b"],      0.080, 0.0006),
 ("Ward x month fixed effects",                lambda: T("extra_robustness.json")["ward_month"]["b"],       0.023, 0.0006),
 ("Pooling city-generated records",            lambda: T("extra_robustness.json")["incl_city_generated"]["b"], 0.055, 0.0006),
 ("Types significant after BH: positive",      lambda: T("multiple_testing.json")["bh_pos"],                25, 0),
 ("Types significant after BH: negative",      lambda: T("multiple_testing.json")["bh_neg"],                5, 0),
 ("Re-report brute-force mismatches",          lambda: T("recurrence_audit.json")["mismatch30"]+T("recurrence_audit.json")["mismatch90"], 0, 0),
 ("PH test p-value for hardship",              lambda: T("ph_test.json")["ph_test"]["hs"]["p"],             0.81, 0.006),
 ("Community-area field matches location",    lambda: 100*T("geo_validation.json")["field_matches_polygon"], 99.34, 0.006),
]
res = {"PASS": 0, "DIFF": 0, "MISSING": 0}
for name, get, exp, tol in C:
    try:
        v = get(); ok = abs(v - exp) <= tol + 1e-12; tag = "PASS" if ok else "DIFF"
        print(f"[{tag:4}] {name:46s} yours={v:>14,.4f}   paper={exp:>12,.4f}")
    except (FileNotFoundError, KeyError) as e:
        tag = "MISSING"; print(f"[MISS] {name:46s} (not produced yet: {e})")
    res[tag] += 1
figs = len(glob.glob(os.path.join(WORK_DIR, "figs", "fig*.png")))
print(f"\nFigures produced: {figs} (paper uses 11)  |  PASS {res['PASS']}  DIFF {res['DIFF']}  MISSING {res['MISSING']}")

# Full comparison of every table cell with the values printed in the paper
exp_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expected", "tables_in_paper.json")
new_f = os.path.join(WORK_DIR, "tables.json")
if os.path.exists(new_f):
    old, new = json.load(open(exp_f)), json.load(open(new_f)); tot = same = 0; diffs = []
    for k in old:
        for i, (a, b) in enumerate(zip(old[k].get("rows", []), new.get(k, {}).get("rows", []))):
            for j, (x, y) in enumerate(zip(a if isinstance(a, list) else [a], b if isinstance(b, list) else [b])):
                tot += 1; same += (x == y)
                if x != y: diffs.append(f"{k} row {i} col {j}: paper={x!r} yours={y!r}")
    print(f"Table cells identical to the paper: {same:,} of {tot:,}")
    for d in diffs[:20]: print("   ", d)
else:
    print("Table cells: run step 22 first to produce work/tables.json")
