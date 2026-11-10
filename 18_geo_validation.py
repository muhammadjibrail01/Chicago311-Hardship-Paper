# Step 18: does the city's community-area field match the point-in-polygon location of each request? (paper: 99.34%)
import json, geopandas as gpd, pyarrow.parquet as pq
r=pq.read_table("core.parquet",columns=["ca","lat","lon"]).to_pandas()
s=r.sample(300_000,random_state=3).dropna(subset=["lat","lon"])
g=gpd.read_file("ca.gpkg")[["ca","geometry"]].rename(columns={"ca":"ca_poly"})
p=gpd.GeoDataFrame(s,geometry=gpd.points_from_xy(s.lon,s.lat),crs=4326)
j=gpd.sjoin(p,g,predicate="within",how="left"); j=j[~j.index.duplicated()]
out={"sample":len(s),"inside_any_polygon":float(j.ca_poly.notna().mean()),"field_matches_polygon":float((j.ca==j.ca_poly).mean())}
json.dump(out,open("tabs/geo_validation.json","w"),indent=1); print(out)
