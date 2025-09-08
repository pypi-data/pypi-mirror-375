# intake_nexgddp/catalog.py
import os

from .config_loader import resolve_visus_home

VISUS_HOME = resolve_visus_home()
print("Using LIB_DIR =", VISUS_HOME)

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List, Iterable

import numpy as np
import pandas as pd
import xarray as xr
import OpenVisus as ov
from intake.source.base import DataSource, Schema

SCENARIO_DATES: Dict[str, Tuple[str, str]] = {
    "historical": ("1950-01-01", "2014-12-31"),
    "ssp126":     ("2015-01-01", "2100-12-31"),
    "ssp245":     ("2015-01-01", "2100-12-31"),
    "ssp370":     ("2015-01-01", "2100-12-31"),
    "ssp585":     ("2015-01-01", "2100-12-31"),
}

AVAILABLE_MODELS: List[str] = [
    "ACCESS-CM2",
    "CanESM5",
    "CESM2",
    "CMCC-CM2-SR5",
    "EC-Earth3",
    "GFDL-ESM4",
    "INM-CM5-0",
    "IPSL-CM6A-LR",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MRI-ESM2-0",
]

AVAILABLE_VARIABLES: List[str] = [
    "hurs", "huss", "pr", "rlds", "rsds", "sfcWind", "tas", "tasmax", "tasmin"
]

AVAILABLE_SCENARIOS: List[str] = ["historical", "ssp126", "ssp245", "ssp370", "ssp585"]

# ----------------------------
# Helpers
# ----------------------------

def _is_leap(y: int) -> bool:
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")

def _day_of_year_365(dt: datetime) -> int:
    """365-day calendar: no Feb 29. For leap years, days after Feb 28 shift by -1."""
    if dt.month == 2 and dt.day == 29:
        raise ValueError("This dataset uses a 365-day calendar (no Feb 29).")
    doy = (dt - datetime(dt.year, 1, 1)).days
    if _is_leap(dt.year) and (dt.month > 2 or (dt.month == 2 and dt.day > 28)):
        doy -= 1
    return doy  # 0..364

def get_timestep_365(date_str: str) -> int:
    dt = _parse_date(date_str)
    return dt.year * 365 + _day_of_year_365(dt)

def _date_seq_365(start: str, end: str) -> List[str]:
    """Inclusive [start,end] on a 365-day calendar. Feb 29 invalid."""
    s = _parse_date(start)
    e = _parse_date(end)
    if e < s:
        raise ValueError(f"end_date {end} is before start_date {start}")
    out: List[str] = []
    cur = s
    while cur <= e:
        if not (cur.month == 2 and cur.day == 29):
            out.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return out

def _coerce_pair(v):
    """Turn YAML list [a,b] or None into a tuple or None."""
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        if len(v) != 2 or v[0] in (None, "None") or v[1] in (None, "None"):
            return None
        return (float(v[0]), float(v[1]))
    return None


class NexGDDPList(DataSource):
    name = "nex_gddp_list"
    version = "1.0"

    def __init__(self, kind: str, **kwargs):
        assert kind in {"models", "variables", "scenarios","timeranges"}
        self.kind = kind
        md = kwargs.pop("metadata", {"kind": kind})
        super().__init__(metadata=md, **kwargs)

    def _load(self) -> pd.DataFrame:
        if self.kind == "models":
            return pd.DataFrame({"model": AVAILABLE_MODELS})
        if self.kind == "variables":
            return pd.DataFrame({"variable": AVAILABLE_VARIABLES})
        if self.kind == "timeranges":
            rows = [{"scenario": s, "start_date": a, "end_date": b}
                    for s, (a, b) in SCENARIO_DATES.items()]
            return pd.DataFrame(rows)
        return pd.DataFrame({"scenario": AVAILABLE_SCENARIOS})

    def read(self) -> pd.DataFrame:
        return self._load()

class NexGDDPTimeline(DataSource):
    name = "nex_gddp_timeranges"
    version = "1.0"

    def __init__(self, **kwargs):
        md = kwargs.pop("metadata", {"source": "scenario_time_ranges"})
        super().__init__(metadata=md, **kwargs)

    def _load(self) -> pd.DataFrame:
        rows = [{"scenario": s, "start_date": a, "end_date": b}
                for s, (a, b) in SCENARIO_DATES.items()]
        return pd.DataFrame(rows)

    def read(self) -> pd.DataFrame:
        return self._load()


class NexGDDPCatalog(DataSource):
    name = "nex_gddp_cmip6"
    version = "1.1"  # bumped

    def __init__(
        self,
        model: str,
        variable: str,
        scenario: str,
        # Single timestamp OR a range OR an explicit list:
        timestamp: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timestamps: Optional[List[str]] = None,

        quality = 0,
        cached = False,
        backup = False,
        lat_range = None,
        lon_range = None,
        **kwargs,
    ):
        self.model = model
        self.variable = variable
        self.scenario = scenario

        self.timestamp = timestamp
        self.start_date = start_date
        self.end_date = end_date
        self.timestamps = timestamps

        self.quality = quality
        self.lat_range = _coerce_pair(lat_range)
        self.lon_range = _coerce_pair(lon_range)
        self.cached = cached
        self.backup = backup

        md = kwargs.pop("metadata", {
            "source": "NEX-GDDP-CMIP6",
            "spatial_resolution": "0.25°",
            "temporal_resolution": "daily (365-day calendar)"
        })
        super().__init__(metadata=md, **kwargs)

    def _get_schema(self) -> Schema:
        return Schema(
            datashape=None, dtype=None, shape=None, npartitions=1,
            extra_metadata={
                "models": AVAILABLE_MODELS,
                "variables": AVAILABLE_VARIABLES,
                "scenarios": AVAILABLE_SCENARIOS,
                "time_ranges": SCENARIO_DATES,
            }
        )

    # ---- list helpers
    def list_models(self):
        return list(AVAILABLE_MODELS)

    def list_variables(self):
        return list(AVAILABLE_VARIABLES)

    def list_scenarios(self):
        return list(AVAILABLE_SCENARIOS)

    def list_timeranges(self):
        return SCENARIO_DATES

    # ---- validation
    def _validate_inputs(self, dates: Iterable[str]):
        if self.model not in AVAILABLE_MODELS:
            raise ValueError(f"Invalid model {self.model}")
        if self.variable not in AVAILABLE_VARIABLES:
            raise ValueError(f"Invalid variable {self.variable}")
        if self.scenario not in AVAILABLE_SCENARIOS:
            raise ValueError(f"Invalid scenario {self.scenario}")
        t0, t1 = SCENARIO_DATES[self.scenario]
        for d in dates:
            if not (t0 <= d <= t1):
                raise ValueError(f"Date {d} outside {t0}..{t1} for scenario {self.scenario}")
            # Feb 29 guard is inside get_timestep_365()

    # ---- time selection logic
    def _resolve_dates(self) -> List[str]:
        if self.timestamps:
            if not isinstance(self.timestamps, (list, tuple)):
                raise ValueError("timestamps must be a list of 'YYYY-MM-DD' strings")
            dates = list(self.timestamps)
        elif self.start_date and self.end_date:
            dates = _date_seq_365(self.start_date, self.end_date)
        elif self.timestamp:
            dates = [self.timestamp]
        else:
            raise ValueError("Provide either timestamp, or start_date+end_date, or timestamps=[...].")
        self._validate_inputs(dates)
        return dates

    # ---- core read for a single timestep; returns (array, lat, lon)
    def _read_one(self, db, field: str, tidx: int,
                  lat_full: np.ndarray, lon_full: np.ndarray,
                  y1: int, y2: int, x1: int, x2: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        logic_box = [[x1, y1], [x2, y2]]  # exclusive upper bound (your original working convention)
        arr = db.read(time=tidx, field=field, quality=self.quality, logic_box=logic_box)

        returned_ny, returned_nx = arr.shape
        # full-res pixel sizes
        lat_pix = lat_full[1] - lat_full[0]
        lon_pix = lon_full[1] - lon_full[0]
        # requested spans (exclusive y2/x2)
        span_y = max(1, y2 - y1)
        span_x = max(1, x2 - x1)
        # decimation stride implied by quality<0
        stride_y = span_y / float(returned_ny)
        stride_x = span_x / float(returned_nx)
        # coordinates
        lat0 = lat_full[y1]
        lon0 = lon_full[x1]
        lat = lat0 + (np.arange(returned_ny) * stride_y * lat_pix)
        lon = lon0 + (np.arange(returned_nx) * stride_x * lon_pix)
        return arr, lat, lon

    # ---- loader
    def _load(self) -> xr.DataArray:
        dates = self._resolve_dates()

        # member special case
        if self.model == "CESM2":
            field = f"{self.variable}_day_{self.model}_{self.scenario}_r4i1p1f1_gn"
        else:
            field = f"{self.variable}_day_{self.model}_{self.scenario}_r1i1p1f1_gn"

        db = ov.LoadDataset('nex-gddp-cmip6')

        # full resolution shape (exclusive upper corner)
        full_nx, full_ny = db.getLogicBox()[1]
        full_nx, full_ny = int(full_nx), int(full_ny)

        # full coordinate vectors
        lat_full = np.linspace(-59.88, 90.0, full_ny, endpoint=False)
        lon_full = np.linspace(0.125, 360.0, full_nx, endpoint=False)

        # default full extent (exclusive)
        y1, y2 = 0, full_ny
        x1, x2 = 0, full_nx

        # apply subset if present (exclusive y2/x2 — your original logic)
        if self.lat_range:
            lat_min, lat_max = self.lat_range
            y1 = int(np.searchsorted(lat_full, lat_min, side="left"))
            y2 = int(np.searchsorted(lat_full, lat_max, side="right"))
        if self.lon_range:
            lon_min, lon_max = self.lon_range
            x1 = int(np.searchsorted(lon_full, lon_min, side="left"))
            x2 = int(np.searchsorted(lon_full, lon_max, side="right"))

        # ---- First read: establish (ny, nx) and lat/lon
        first_tidx = get_timestep_365(dates[0])
        first_arr, lat, lon = self._read_one(db, field, first_tidx, lat_full, lon_full, y1, y2, x1, x2)
        ny_r, nx_r = first_arr.shape

        if len(dates) == 1:
            # Single day: return 2D DataArray
            return xr.DataArray(first_arr, coords=[("lat", lat), ("lon", lon)])

        # ---- Multi-day: preallocate and fill (time, lat, lon)
        out = np.empty((len(dates), ny_r, nx_r), dtype=first_arr.dtype)
        out[0] = first_arr

        for i, ds in enumerate(dates[1:], start=1):
            tidx = get_timestep_365(ds)
            arr_i, lat_i, lon_i = self._read_one(db, field, tidx, lat_full, lon_full, y1, y2, x1, x2)
            # sanity: shape must match (same quality, same box)
            if arr_i.shape != (ny_r, nx_r):
                raise RuntimeError(f"Shape changed across timesteps: {arr_i.shape} vs {(ny_r, nx_r)}. "
                                   "Check quality/box consistency.")
            # we also expect consistent lat/lon across days
            out[i] = arr_i

        # build time coordinate (numpy datetime64[D] from strings)
        time_coord = np.array(dates, dtype="datetime64[D]")

        return xr.DataArray(out, coords=[("time", time_coord), ("lat", lat), ("lon", lon)])

    def read(self) -> xr.DataArray:
        return self._load()
