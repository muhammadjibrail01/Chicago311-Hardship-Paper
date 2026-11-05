"""Settings for the Paper 1 replication package. Edit the three folders here or set them as environment variables."""
import os
HERE=os.path.dirname(os.path.abspath(__file__))
RAW_DIR=os.environ.get("RAW_DIR", os.path.join(HERE,"raw_data"))                                   # downloads (Census tables, boundaries, HRI, HOLC map, crime, building violations)
MAIN_WORK=os.environ.get("MAIN_WORK", os.path.join(HERE,"..","chicago311_replication","work"))     # work folder of the main-paper package (run it first)
WORK_DIR=os.environ.get("WORK_DIR", os.path.join(HERE,"work"))                                     # outputs of this package
U=RAW_DIR.rstrip("/")+"/"; MAIN=MAIN_WORK.rstrip("/")+"/"; W=WORK_DIR.rstrip("/")+"/"; D=W+"data/"
