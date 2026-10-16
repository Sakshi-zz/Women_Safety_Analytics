import os
import json
import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# ---------- Hardcoded paths (no glob, no guessing) ----------
CSV_PATH = "/workspaces/Major_project/data/processed/district_level_data.csv"
CACHE_PATH = "/workspaces/Major_project/data/raw/geocode_cache.json"

print(f"📂 Loading: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"   {len(df)} rows, {len(df.columns)} columns")

# ---------- Load cache ----------
cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    print(f"📦 Loaded {len(cache)} cached coordinates")

# ---------- Setup geocoder ----------
geolocator = Nominatim(user_agent="women_safety_project_sakshi")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

# ---------- Get unique districts ----------
unique = df[["state_name", "district_name"]].drop_duplicates()
print(f"📍 Processing {len(unique)} unique districts...")

missing_count = 0
for i, (_, row) in enumerate(unique.iterrows()):
    key = f"{row['state_name']}|{row['district_name']}"
    if key in cache:
        continue

    query = f"{row['district_name']}, {row['state_name']}, India"
    try:
        loc = geocode(query)
        if loc:
            cache[key] = [loc.latitude, loc.longitude]
        else:
            cache[key] = [None, None]
            missing_count += 1
    except Exception as e:
        print(f"   ⚠️  Failed: {query} — {e}")
        cache[key] = [None, None]
        missing_count += 1

    if (i + 1) % 25 == 0:
        print(f"   Progress: {i + 1}/{len(unique)}")
        with open(CACHE_PATH, "w") as f:
            json.dump(cache, f)

# Save final cache
with open(CACHE_PATH, "w") as f:
    json.dump(cache, f)

# ---------- Apply coordinates to DataFrame ----------
def get_coord(row, idx):
    key = f"{row['state_name']}|{row['district_name']}"
    return cache.get(key, [None, None])[idx]

df["latitude"] = df.apply(lambda r: get_coord(r, 0), axis=1)
df["longitude"] = df.apply(lambda r: get_coord(r, 1), axis=1)

# ---------- Report ----------
matched = df["latitude"].notna().sum()
print()
print("=" * 60)
print(f"✅ Matched: {matched}/{len(df)} ({100 * matched / len(df):.1f}%)")
print(f"❌ Unmatched: {len(df) - matched}")
print("=" * 60)

# ---------- Save ----------
df.to_csv(CSV_PATH, index=False)
print(f"💾 Saved to: {CSV_PATH}")

# ---------- Verify the save actually worked ----------
verify = pd.read_csv(CSV_PATH)
print(f"🔍 Verification — latitude column exists: {'latitude' in verify.columns}")
if "latitude" in verify.columns:
    print(f"🔍 Verification — non-null latitudes: {verify['latitude'].notna().sum()}")