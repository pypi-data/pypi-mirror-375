import os
import warnings
import zipfile
from typing import Dict, Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path


class IllegalParking:
    """
    Identify illegal parking points using geopandas.sjoin on GIS layers.

    Assumptions
    -----------
    - All layers & points use CRS = EPSG:4326 (WGS84).
    - Input has a 'Geometry' column containing shapely Points or 'POINT(lon lat)' strings.
    - Duration threshold rules:
        * >= 5 min within {custom_area | yellow_solid | yellow_dashed}
        * >= 1 min within {crosswalk | sidewalk | yellow_double} AND not within custom_area

    Output columns:
      ['CCTV_ID', 'time', 'Geometry', 'Leaving_time', 'Traj_ID', 'Duration', 'ufid']

    Parameters
    ----------
    zip_path : str
        Path to a .zip file containing SHP files.
    extract_dir : str
        Directory where SHP files are extracted.
    layer_keys : dict, optional
        Logical name -> SHP base filename (without .shp).
    """

    def __init__(
        self,
        zip_path: str,
        extract_dir: str,
        layer_keys: Optional[Dict[str, str]] = None,
    ) -> None:
        
        zp = Path(zip_path).expanduser()
        ed = Path(extract_dir).expanduser()
        if not zp.is_absolute():
            zp = Path.cwd() / zp
        if not ed.is_absolute():
            ed = Path.cwd() / ed

        self.zip_path = zp
        self.extract_dir = ed
        self.layer_keys = layer_keys or {
            "custom_area": "custom_area_4326",
            "cross_walk": "crosswalk_4326",
            "side_walk": "sidewalk_4326",
            "buffer_ye_double": "ye_double_bf_4326",
            "buffer_ye_solid": "ye_solid_bf_4326",
            "buffer_ye_dashed": "ye_dashed_bf_4326",
        }
        self.gdf_layers = self._load_and_extract_layers()

    # ------------------------- helpers ------------------------- #
    def _load_and_extract_layers(self) -> Dict[str, gpd.GeoDataFrame]:
        """Unzip and load shapefiles; ensure CRS=EPSG:4326."""

        if not self.zip_path.exists():
            raise FileNotFoundError(
                f"Zip file does not exist: {self.zip_path}\n"
                f"(cwd: {Path.cwd()})"
            )

        self.extract_dir.mkdir(parents=True, exist_ok=True)

        # unzip
        with zipfile.ZipFile(self.zip_path, "r") as zf:
            zf.extractall(self.extract_dir)

        layers: Dict[str, gpd.GeoDataFrame] = {}
        for key, base in self.layer_keys.items():
            shp = self.extract_dir / f"{base}.shp"  # ✅ Path 사용
            if not shp.exists():
                raise FileNotFoundError(f"Missing SHP for '{key}': {shp}")
            gdf = gpd.read_file(str(shp))
            if gdf.crs is None:
                warnings.warn(f"Layer '{key}' has no CRS; assuming EPSG:4326.")
                gdf.set_crs(epsg=4326, inplace=True)
            elif gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)
            layers[key] = gdf
        return layers

    @staticmethod
    def _parse_point(value):
        """Parse 'POINT(lon lat)' to Point; passthrough if already Point."""
        if isinstance(value, Point):
            return value
        if isinstance(value, str) and value.startswith("POINT("):
            try:
                lon, lat = value.replace("POINT(", "").replace(")", "").split()
                return Point(float(lon), float(lat))
            except Exception:
                return None
        return None

    @staticmethod
    def _flag_within(points: gpd.GeoDataFrame, polys: gpd.GeoDataFrame) -> pd.Series:
        """
        Return boolean Series aligned to points.index, True if point is within any polygon.
        Uses geopandas.sjoin(predicate='within') and reduces multiple hits via any().
        """
        left = points[["Geometry"]].reset_index()  # keep original index
        joined = gpd.sjoin(left, polys[["geometry"]], how="left", predicate="within")
        flags = joined.groupby("index")["index_right"].apply(lambda s: s.notna().any())
        return flags.reindex(points.index, fill_value=False)

    # --------------------------- API --------------------------- #
    def analyze(self, frequent_parking_result: pd.DataFrame) -> pd.DataFrame:
        """Apply rule-based illegal parking detection using spatial joins."""
        if frequent_parking_result is None:
            raise ValueError("frequent_parking_result must not be None.")

        if frequent_parking_result.empty or "Geometry" not in frequent_parking_result.columns:
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        gdf = frequent_parking_result.copy()

        # Ensure shapely Point geometry
        if gdf["Geometry"].dtype == object:
            gdf["Geometry"] = gdf["Geometry"].apply(self._parse_point)
        gdf.dropna(subset=["Geometry"], inplace=True)
        if gdf.empty:
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        gdf = gpd.GeoDataFrame(gdf, geometry="Geometry", crs="EPSG:4326")

        # Ensure Duration is Timedelta and compute minutes
        if not pd.api.types.is_timedelta64_dtype(gdf["Duration"]):
            try:
                gdf["Duration"] = pd.to_timedelta(gdf["Duration"])
            except Exception:
                warnings.warn("Could not convert 'Duration' to Timedelta.")
        gdf["duration_minutes"] = gdf["Duration"].dt.total_seconds() / 60.0

        # sjoin-based boolean flags
        in_custom_area = self._flag_within(gdf, self.gdf_layers["custom_area"])
        in_cross_walk = self._flag_within(gdf, self.gdf_layers["cross_walk"])
        in_side_walk = self._flag_within(gdf, self.gdf_layers["side_walk"])
        in_buffer_double = self._flag_within(gdf, self.gdf_layers["buffer_ye_double"])
        in_buffer_solid = self._flag_within(gdf, self.gdf_layers["buffer_ye_solid"])
        in_buffer_dashed = self._flag_within(gdf, self.gdf_layers["buffer_ye_dashed"])

        dur = gdf["duration_minutes"].fillna(0)

        # Rule set
        illegal_5 = (dur >= 5) & (in_custom_area | in_buffer_solid | in_buffer_dashed)
        illegal_1 = (dur >= 1) & (in_cross_walk | in_side_walk | in_buffer_double) & (~in_custom_area)

        mask = illegal_5 | illegal_1
        if not mask.any():
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        sel = gdf.loc[mask].drop_duplicates()

        return pd.DataFrame(
            {
                "CCTV_ID": sel["CCTV_ID"],
                "time": sel["time"],
                "Geometry": sel["Geometry"],
                "Leaving_time": sel["Leaving_time"],
                "Traj_ID": sel["Traj_ID"],
                "Duration": sel["Duration"],
                "ufid": sel["ufid"],
            }
        )

    def call(self, frequent_parking_result: pd.DataFrame) -> pd.DataFrame:
        """Alias for analyze()."""
        return self.analyze(frequent_parking_result)

