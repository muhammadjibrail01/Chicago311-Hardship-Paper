# Step 17: audit of the origin -> channel coding for the 49 core request types (volume, instant closures, duplicates, dates).
import pandas as pd, pyarrow.parquet as pq
r=pq.read_table("req.parquet",columns=["type","origin","created","closed","dup"],read_dictionary=["type","origin"]).to_pandas()
core=pd.read_csv("tabs/core_types.csv").iloc[:,0].tolist(); r=r[r.type.isin(core)]
PHONE={"Phone Call","Phone","Walk-in","Mail","Fax"}
DIGI={"Internet","Web","Mobile Device","E-Mail","Social Media","Open311","Open311 Interface","Spot311 Interface","SPOT311"}
ALD={"Alderman's Office","ALDERMAN","State Representatives","Mayor's Office","Budget Town Hall Meeting","FY25 Budget Engagement"}
ch=lambda o: "phone" if o in PHONE else "digital" if (o in DIGI or o.startswith("spot-open311")) else "alderman" if o in ALD else "city"
r["hrs"]=(r.closed-r.created).dt.total_seconds()/3600
g=r.groupby("origin",observed=True).agg(n=("dup","size"),dup_share=("dup","mean"),instant_close_share=("hrs",lambda s:(s<=1/60).mean()),
   median_hours=("hrs","median"),first=("created","min"),last=("created","max")).sort_values("n",ascending=False)
g["channel"]=[ch(o) for o in g.index]; g.to_csv("tabs/channel_audit.csv"); print(g.head(12).round(3).to_string())
