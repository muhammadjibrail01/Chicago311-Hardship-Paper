"""Run the whole analysis in order:  python run_all.py            (all steps)
                                     python run_all.py --from 7  (resume from step 7)
                                     python run_all.py --only 12 (one step)
Each step runs inside WORK_DIR (outputs: tabs/, figs/, logs/, data/); logs are written to WORK_DIR/logs/."""
import argparse, glob, os, subprocess, sys, time
from config import WORK_DIR
HERE=os.path.dirname(os.path.abspath(__file__)); CODE=os.path.join(HERE,"code")
ap=argparse.ArgumentParser(); ap.add_argument("--from",dest="start",type=int,default=0); ap.add_argument("--only",type=int); a=ap.parse_args()
for d in ["", "tabs", "figs", "logs", "data"]: os.makedirs(os.path.join(WORK_DIR,d), exist_ok=True)
env=dict(os.environ, PYTHONPATH=os.pathsep.join([HERE, CODE, os.environ.get("PYTHONPATH","")]), MPLBACKEND="Agg")
steps=sorted(glob.glob(os.path.join(CODE,"[0-9][0-9]_*.py")))
for s in steps:
    k=int(os.path.basename(s)[:2])
    if (a.only is not None and k!=a.only) or k<a.start: continue
    t=time.time(); log=os.path.join(WORK_DIR,"logs",os.path.basename(s).replace(".py",".log"))
    with open(log,"w") as fh: rc=subprocess.run([sys.executable,s],cwd=WORK_DIR,env=env,stdout=fh,stderr=subprocess.STDOUT).returncode
    print(f"[{'OK ' if rc==0 else 'FAIL'}] {os.path.basename(s):50s} {time.time()-t:7.1f}s   log: {log}", flush=True)
    if rc!=0:
        if rc<0 or rc==137: print("The system stopped this step (usually because the computer ran out of memory). Close other programs and resume with --from", k)
        else: print("Stopped. Open the log above to see the error, fix it, then resume with --from", k)
        sys.exit(1)
print("All steps finished. Next: python check_results.py")
