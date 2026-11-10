"""Settings for the replication package. Edit RAW_DIR / WORK_DIR here, or set them as environment variables."""
import os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.environ.get("RAW_DIR", os.path.join(HERE, "raw_data"))    # folder with the downloaded Chicago Data Portal files
WORK_DIR = os.environ.get("WORK_DIR", os.path.join(HERE, "work"))      # all intermediate files, results, and figures go here
START, END = "2019-01-01", "2024-12-31"                                  # study window used in the paper
def raw_files(pattern):
    """All raw files matching a pattern (searched in RAW_DIR and in WORK_DIR/311_csv for extracted archives)."""
    return sorted(set(glob.glob(os.path.join(RAW_DIR, pattern)) + glob.glob(os.path.join(WORK_DIR, "311_csv", pattern))))
def raw_one(pattern):
    f = raw_files(pattern)
    if not f: raise FileNotFoundError(f"No file matching '{pattern}' in {RAW_DIR}. See README section 2.")
    return f[0]
