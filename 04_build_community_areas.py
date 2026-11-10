# Step 4: community-area covariates: Hardship Index (2008-2012), ACS 2019-2023, violent crime (deduplicated),
# building violations (spatially joined), area, density, distance to the Loop, hardship quartiles.
import pandas as pd, numpy as np, geopandas as gpd
from shapely import wkt
from config import raw_one, raw_files, START, END
b = pd.read_csv(raw_one("Boundaries*Community*Areas*.csv"))
b["geometry"] = b["the_geom"].apply(wkt.loads)
g = gpd.GeoDataFrame(b[["AREA_NUMBE","COMMUNITY"]].rename(columns={"AREA_NUMBE":"ca","COMMUNITY":"name"}), geometry=b["geometry"], crs=4326)
g["ca"]=g.ca.astype(int); gp = g.to_crs(26916)
g["area_km2"] = gp.area/1e6
cent = gp.centroid; loop = cent[g.ca==32].iloc[0]
g["dist_loop_km"] = cent.distance(loop)/1000
c = pd.read_csv(raw_one("Census_Data*Selected_socioeconomic*.csv")).dropna(subset=["Community Area Number"])
c.columns=["ca","cname","crowded","poverty","unemp","nohs","dependency","pci","hardship"]; c["ca"]=c.ca.astype(int)
a = pd.read_csv(raw_one("ACS_5_Year_Data_by_Community_Area*.csv"), thousands=",")
print("ACS years:", a["ACS Year"].unique(), len(a))
a["key"]=a["Community Area"].str.upper().str.replace("[^A-Z]","",regex=True)
g["key"]=g.name.str.upper().str.replace("[^A-Z]","",regex=True)
inc=["Under $25,000","$25,000 to $49,999","$50,000 to $74,999","$75,000 to $125,000","$125,000 +"]
a["hh"]=a[inc].sum(1); a["lowinc"]=100*a["Under $25,000"]/a.hh; a["highinc"]=100*a["$125,000 +"]/a.hh
P=a["Total Population"]; a["pop"]=P
a["pct_black"]=100*a["Black or African American"]/P; a["pct_hisp"]=100*a["Hispanic or Latino"]/P
a["pct_nhwhite"]=100*a["White Not Hispanic or Latino"]/P; a["pct_asian"]=100*a["Asian"]/P
a["pct_65"]=100*(a["Male 65+"]+a["Female 65 +"])/P
m = g.merge(a[["key","pop","hh","lowinc","highinc","pct_black","pct_hisp","pct_nhwhite","pct_asian","pct_65"]], on="key", how="left")
print("ACS unmatched community areas:", m[m["pop"].isna()].name.tolist())
m = m.merge(c, on="ca", how="left"); m["density"]=m["pop"]/m.area_km2
fs = raw_files("Crimes*2001_to_Present*.csv")
cr = pd.concat([pd.read_csv(f, usecols=["ID","FBI Code","Community Area","Year"], dtype={"FBI Code":str}) for f in fs])
n0=len(cr); cr=cr.drop_duplicates("ID"); cr=cr[cr.Year.between(int(START[:4]),int(END[:4]))]
print(f"crime files {len(fs)}: rows {n0:,} -> unique incidents in window {len(cr):,}")
cr["viol"]=cr["FBI Code"].isin(["01A","02","03","04A","04B"])
cc = cr.groupby("Community Area").agg(crimes=("ID","size"), violent=("viol","sum")).reset_index().rename(columns={"Community Area":"ca"})
m = m.merge(cc, on="ca", how="left"); nyrs = cr.Year.nunique()
m["crime_rate"]=1000*m.crimes/m["pop"]/nyrs; m["viol_rate"]=1000*m.violent/m["pop"]/nyrs
bv = pd.concat([pd.read_csv(f, usecols=["ID","VIOLATION DATE","INSPECTION CATEGORY","LATITUDE","LONGITUDE"]) for f in raw_files("Building_Violations*.csv")]).drop_duplicates("ID")
vd = pd.to_datetime(bv["VIOLATION DATE"], errors="coerce"); bv = bv[(vd>=START)&(vd<pd.Timestamp(END)+pd.Timedelta(days=1))]
bv=bv.dropna(subset=["LATITUDE","LONGITUDE"]); print(f"building violations geocoded in window: {len(bv):,}")
bg = gpd.GeoDataFrame(bv, geometry=gpd.points_from_xy(bv.LONGITUDE,bv.LATITUDE), crs=4326)
j = gpd.sjoin(bg, g[["ca","geometry"]], predicate="within"); print(f"joined to community areas: {len(j):,}")
bvc = j.groupby("ca").agg(bviol=("ID","size"), bviol_complaint=("INSPECTION CATEGORY", lambda s:(s=="COMPLAINT").sum())).reset_index()
bvc.to_csv("bviol_by_ca.csv", index=False)
m = m.merge(bvc, on="ca", how="left"); m["bviol_rate"]=1000*m.bviol/m["pop"]/6
m["hq"]=pd.qcut(m.hardship.rank(method="first"),4,labels=[1,2,3,4]).astype(int)
m.to_file("ca.gpkg", driver="GPKG"); m.drop(columns="geometry").to_csv("ca.csv", index=False)
print("hardship mean/sd:", round(m.hardship.mean(),2), round(m.hardship.std(),2), "| quartile sizes:", m.hq.value_counts().sort_index().to_dict())
