import warnings
from typing import Optional

import numpy as np
import pandas as pd


class FrequentParking:
    """
    Detect habitual/frequent parking stays from trajectory detections.

    This version supports flexible schemas:
      - Path A: mf_* schema (e.g., 'mf_type', 'mf_id')
      - Path B: obj_* schema (e.g., 'obj_cd', 'obj_id')
      - If a 'geometry' (Point) column exists, 'lon'/'lat' are auto-derived when missing.

    Output columns:
      ['CCTV_ID', 'time', 'Geometry', 'Leaving_time', 'Traj_ID', 'Duration', 'ufid']

    Parameters
    ----------
    input_df : pd.DataFrame
        Detection records; must include time & id columns based on schema.
    road_df : pd.DataFrame
        CCTV mapping with columns ['CCTV_ID', 'ufid'].
    spatial_radius_km : float, default=0.00235
        Cluster radius in kilometers (~2.35 meters).
    min_stop_minutes : float, default=1.0
        Minimum stay duration to be considered a "stay".
    min_report_minutes : int, default=5
        Minimum duration to be reported in the final output.
    min_n_locations : int, default=1
        Minimum number of points in a cluster.
    """

    # For obj_* schema: object codes considered "vehicle"
    TARGET_OBJ_CODES = {"M0301", "M0302", "M0309", "M0307", "M0308", "M0303", "M0304", "M0305", "M0306"}

    def __init__(
        self,
        input_df: pd.DataFrame,
        road_df: pd.DataFrame,
        spatial_radius_km: float = 0.00235,
        min_stop_minutes: float = 1.0,
        min_report_minutes: int = 5,
        min_n_locations: int = 1,
    ) -> None:
        self.input_df = input_df.copy()
        self.road_df = road_df.copy()
        self.spatial_radius_km = spatial_radius_km
        self.min_stop_minutes = min_stop_minutes
        self.min_report_minutes = min_report_minutes
        self.min_n_locations = min_n_locations

    # --------------------------- helpers --------------------------- #
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Return great-circle distance (km) between two (lat, lon) arrays."""
        R = 6371.0
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(np.clip(1.0 - a, 0, 1)))
        return R * c

    def _detect_stay_locations_manual_performance_only(self, df_vehicles: pd.DataFrame) -> pd.DataFrame:
        """
        Greedy clustering within spatial radius; marks a stay if duration >= min_stop_minutes.
        Supports mf_* or obj_* schema for the unique id column.
        """
        if "mf_type" in df_vehicles.columns:
            id_col = "mf_id"
            required_cols = ["dtct_dt", "mf_id", "lon", "lat", "snr_id"]
        elif "obj_cd" in df_vehicles.columns:
            id_col = "obj_id"
            required_cols = ["dtct_dt", "obj_id", "lon", "lat", "snr_id"]
        else:
            warnings.warn("Missing identifier schema (mf_* or obj_*). Returning empty DataFrame.")
            return pd.DataFrame()

        for col in required_cols:
            if col not in df_vehicles.columns:
                warnings.warn(f"Missing required column: {col}. Returning empty DataFrame.")
                return pd.DataFrame()

        df_vehicles = df_vehicles.sort_values(by=[id_col, "dtct_dt"]).reset_index(drop=True)
        stays = []

        for uid, user_df in df_vehicles.groupby(id_col):
            user_df = user_df.reset_index(drop=True)
            lats = user_df["lat"].values
            lons = user_df["lon"].values
            times = user_df["dtct_dt"].values
            snr_ids = user_df["snr_id"].values

            i = 0
            while i < len(user_df):
                potential = [i]
                current_snr_id = snr_ids[i]
                j = i + 1

                while j < len(user_df):
                    temp_idx = potential + [j]
                    temp_lats = lats[temp_idx]
                    temp_lons = lons[temp_idx]
                    center_lat = np.mean(temp_lats)
                    center_lon = np.mean(temp_lons)
                    max_dist = np.max(self._haversine_distance(center_lat, center_lon, temp_lats, temp_lons))
                    if max_dist <= self.spatial_radius_km:
                        potential.append(j)
                        j += 1
                    else:
                        break

                end_idx = j - 1
                if len(potential) >= self.min_n_locations and end_idx >= i:
                    start_t = times[i]
                    end_t = times[end_idx]
                    duration = (
                        end_t - start_t
                        if isinstance(start_t, pd.Timestamp)
                        else pd.Timedelta(end_t - start_t)
                    )
                    if duration >= pd.Timedelta(minutes=self.min_stop_minutes):
                        stays.append(
                            {
                                "datetime": start_t,
                                "leaving_datetime": end_t,
                                "lat": float(np.mean(lats[i:j])),
                                "lng": float(np.mean(lons[i:j])),
                                "uid": uid,
                                "snr_id": current_snr_id,
                                "duration": duration,
                            }
                        )
                        i = j
                    else:
                        i += 1
                else:
                    i += 1

        return pd.DataFrame(stays)

    def _prepare_and_detect_stay_locations(self, df_cctv: pd.DataFrame, cctv_id: Optional[str]) -> pd.DataFrame:
        """
        Filter detections to vehicles, standardize lon/lat if geometry exists,
        then run stay detection.
        """
        if "mf_type" in df_cctv.columns:
            df_vehicles = df_cctv[df_cctv["mf_type"] == 2].copy()
            # ensure mf_id exists if only obj_id present
            if "mf_id" not in df_vehicles.columns and "obj_id" in df_vehicles.columns:
                df_vehicles["mf_id"] = df_vehicles["obj_id"]
            # derive lon/lat from geometry if needed
            if "geometry" in df_vehicles.columns and ("lon" not in df_vehicles.columns or "lat" not in df_vehicles.columns):
                df_vehicles["lon"] = df_vehicles["geometry"].apply(lambda p: p.x)
                df_vehicles["lat"] = df_vehicles["geometry"].apply(lambda p: p.y)

        elif "obj_cd" in df_cctv.columns:
            df_vehicles = df_cctv[df_cctv["obj_cd"].isin(self.TARGET_OBJ_CODES)].copy()
            if "geometry" in df_vehicles.columns and ("lon" not in df_vehicles.columns or "lat" not in df_vehicles.columns):
                df_vehicles["lon"] = df_vehicles["geometry"].apply(lambda p: p.x)
                df_vehicles["lat"] = df_vehicles["geometry"].apply(lambda p: p.y)

        else:
            warnings.warn(f"CCTV_ID {cctv_id}: neither 'mf_type' nor 'obj_cd' present. Returning empty.")
            return pd.DataFrame()

        if df_vehicles.empty:
            return pd.DataFrame()

        return self._detect_stay_locations_manual_performance_only(df_vehicles)

    # ---------------------------- API ----------------------------- #
    def analyze(self) -> pd.DataFrame:
        """Run per-CCTV, per-hour frequent parking detection."""
        if self.input_df is None or self.input_df.empty:
            warnings.warn("input_df is empty. Returning empty DataFrame.")
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        temp_df = self.input_df.copy()

        # Normalize dtct_dt into a proper datetime column
        if "dtct_dt" in temp_df.columns and not pd.api.types.is_datetime64_any_dtype(temp_df["dtct_dt"]):
            temp_df["dtct_dt"] = pd.to_datetime(temp_df["dtct_dt"], format="mixed", errors="coerce")
            temp_df.dropna(subset=["dtct_dt"], inplace=True)

        if temp_df.empty:
            warnings.warn("After dtct_dt parsing, input became empty. Returning empty.")
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        if "snr_id" not in temp_df.columns:
            warnings.warn("Missing 'snr_id' (CCTV ID). Returning empty.")
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        # CCTV -> ufid map
        cctv_ufid_map = (
            self.road_df[["CCTV_ID", "ufid"]]
            .drop_duplicates(subset=["CCTV_ID"], keep="first")
            .rename(columns={"CCTV_ID": "snr_id"})
        )

        all_results = []
        for cctv_id, df_cctv_original in temp_df.groupby("snr_id"):
            df_cctv = df_cctv_original.copy()
            if "dtct_dt" not in df_cctv.columns:
                warnings.warn(f"CCTV_ID {cctv_id}: missing 'dtct_dt'. Skipping.")
                continue

            df_cctv["hour"] = df_cctv["dtct_dt"].dt.floor("h")
            for _, df_hour in df_cctv.groupby("hour"):
                stdf = self._prepare_and_detect_stay_locations(df_hour, cctv_id)
                if stdf.empty:
                    continue

                stdf = stdf[stdf["duration"] >= pd.Timedelta(minutes=self.min_report_minutes)].copy()
                if stdf.empty:
                    continue

                stdf_merged = stdf.merge(cctv_ufid_map, on="snr_id", how="left")
                out = pd.DataFrame(
                    {
                        "CCTV_ID": stdf_merged["snr_id"],
                        "time": stdf_merged["datetime"],
                        "Geometry": stdf_merged.apply(lambda r: f"POINT({r['lng']} {r['lat']})", axis=1),
                        "Leaving_time": stdf_merged["leaving_datetime"],
                        "Traj_ID": stdf_merged["uid"].astype("int64"),
                        "Duration": stdf_merged["duration"],
                        "ufid": stdf_merged["ufid"],
                    }
                )
                all_results.append(out)

        if not all_results:
            return pd.DataFrame(columns=["CCTV_ID", "time", "Geometry", "Leaving_time", "Traj_ID", "Duration", "ufid"])

        final = pd.concat(all_results, ignore_index=True).drop_duplicates()
        return final

    def call(self) -> pd.DataFrame:
        """Alias of analyze()."""
        return self.analyze()
