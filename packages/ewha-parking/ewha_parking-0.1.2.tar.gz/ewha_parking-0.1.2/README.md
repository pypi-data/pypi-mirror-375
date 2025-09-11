# ewha-parking

A Python module for detecting **Frequent Parking** spots from CCTV trajectory data  
and identifying **Illegal Parking** events using GIS layers.

---

## How to use

```python
from ewha_parking.frequent_parking import FrequentParking
from ewha_parking.illegal_parking import IllegalParking

# df: trajectory data (required fields: snr_id, traj_id, dtct_dt, lon/lat or geometry)
# road_df: road data (required fields: CCTV_ID, ufid, geometry)

# frequent parking
frequent_result = FrequentParking(df.copy(), road_df).call()

# illegal parking
illegal_parking = IllegalParking(
    zip_path="data/illegal_parking.zip",          # ZIP archive containing SHP files
    extract_dir="data/illegal_parking_extracted"  # Directory to extract SHP files
)
illegal_result = illegal_parking.call(frequent_result)

## Output

- **FrequentParking result**
  - Columns: `CCTV_ID`, `time`, `Geometry`, `Leaving_time`, `Traj_ID`, `Duration`, `ufid`

- **IllegalParking result**
  - Subset of the above events flagged as illegal
  - Rules:
    - ≥ 5 minutes: within custom_area, yellow solid line, yellow dashed line, etc.
    - ≥ 1 minute: within crosswalk, sidewalk, yellow double line (excluding custom_area)


## Requirements
pandas, numpy, geopandas, shapely

> All SHP layers are assumed to use EPSG:4326 (WGS84).
> If your data uses a different CRS, please reproject it before analysis.

## License
This project is licensed under JiwonKim License.

## Contact
kimjiwon4007@ewha.ac.kr