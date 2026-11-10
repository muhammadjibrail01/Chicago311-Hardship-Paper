# Step 3: profile every request type (volume, department, status, duplicates, completion time).
from common import *
r=load(); r["hrs"]=(r.closed-r.created).dt.total_seconds()/3600
g=r.groupby("type",observed=True)
t=pd.DataFrame({"n":g.size(),"dept":g.dept.agg(lambda s:s.mode().iat[0]),"dup%":100*g.dup.mean(),
 "cmp%":100*g.status.agg(lambda s:(s=="Completed").mean()),"can%":100*g.status.agg(lambda s:(s=="Canceled").mean()),
 "open%":100*g.status.agg(lambda s:(s=="Open").mean()),"med_h":g.hrs.median(),
 "zero%":100*g.hrs.agg(lambda s:(s<=1/60).mean()),"neg%":100*g.hrs.agg(lambda s:(s<0).mean())}).sort_values("n",ascending=False)
t.to_csv("tabs/type_profile.csv")
