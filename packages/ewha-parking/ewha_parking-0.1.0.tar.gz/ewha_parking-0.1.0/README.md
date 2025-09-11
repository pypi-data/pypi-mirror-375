#### **README.md**



**## ewha-parking**

A Python package for analyzing **frequent parking** and **illegal parking** using trajectory data and GIS layers.

* Detects **Frequent Parking** spots from trajectory data.
* Identifies **Illegal Parking** candidates by comparing detected spots against sidewalks, crosswalks, and yellow line buffer zones.





**## Installation**

After uploading to PyPI: pip install ewha-parking

For local development: pip install -e .





**## Usage**

import time

import pandas as pd

from ewha\_parking.frequent\_parking import FrequentParking

from ewha\_parking.illegal\_parking import IllegalParking



\# Load input data

df, road\_df



start = time.perf\_counter()



\# 1. Detect frequent parking spots

frequent\_parking = FrequentParking(df.copy(), road\_df)

frequent\_result = frequent\_parking.call()



\# 2. Detect illegal parking

illegal\_parking = IllegalParking(

&nbsp;   zip\_path="illegal\_parking.zip",          # ZIP archive containing SHP files

&nbsp;   extract\_dir="illegal\_parking\_extracted"  # Directory to extract SHP files

)

illegal\_result = illegal\_parking.call(frequent\_result)



end = time.perf\_counter()

print(f"Execution time: {end - start:.2f} seconds")



\# Example output DataFrame columns:

\# \['CCTV\_ID', 'time', 'Geometry', 'Leaving\_time', 'Traj\_ID', 'Duration', 'ufid']





**## Requirements**

* Python >= 3.9
* pandas
* numpy
* geopandas
* shapely (>= 2.0 recommended)



Note: SHP layers are assumed to use EPSG:4326 (WGS84).

If your data uses a different CRS, please convert it before analysis.





**## License**

MIT License (?)





**## Author**

* Name: Jiwon Kim
* Email: kimjiwon4007@ewha.ac.kr
