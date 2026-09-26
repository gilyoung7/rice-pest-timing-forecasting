import os
from pathlib import Path


# Raw data lives outside git (see DATA.md). RICE_DATA_ROOT is the directory that mirrors the
# original server's data root (it contains rice/<daily csv> and rice/LONG_by_pest/); default
# <repo>/data, e.g. a symlink to shared storage. Handoff change: only the default location moved
# (originally the absolute path of the first server); file names and contents are unchanged.
DATA_ROOT = Path(os.environ.get("RICE_DATA_ROOT", Path(__file__).resolve().parents[2] / "data"))

# The daily union table. RICE_DAILY_CSV overrides this single file (canonical training via
# vendor/_patched_train.py aborts if it is set; use RICE_DATA_ROOT instead).
PATH_DAILY = Path(os.environ.get(
    "RICE_DAILY_CSV",
    DATA_ROOT / "rice" / "1997_2024_RICE_union_all_sites_with_GDD10_since_gs.csv"))
YEAR_MIN = None
YEAR_MAX = 2024

# Directory holding the per-pest observation tables (RICE_LONG_<korean name>.csv). Each pest
# config joins its own filename onto this, so the Korean pest name stays in that pest's config.
# RICE_LONG_BY_PEST_DIR overrides it (same training-guard caveat as RICE_DAILY_CSV).
LONG_BY_PEST_DIR = Path(os.environ.get(
    "RICE_LONG_BY_PEST_DIR", DATA_ROOT / "rice" / "LONG_by_pest"))

# Always shared across all pests to avoid duplicated caches.
RICE_ROOT = Path(__file__).resolve().parents[1]
DAILY_CACHE_DIR = RICE_ROOT / "outputs" / "cache"

# Cache/version controls for daily preprocessing.
PREPROC_VERSION = "v1.0"
IMPUTE_POLICY = "ffill_bfill_interpolate_fill0"
MISS_INDICATOR_POLICY = "enabled"
