# intake_nexgddp/config_loader.py
import os
from pathlib import Path
from importlib.resources import files, as_file  # Python 3.9+
# If you need 3.8 support: from importlib_resources import files, as_file

PKG = "intake_nexgddp"

# intake_nexgddp/config_loader.py (or wherever you set this)
import os
from pathlib import Path
from importlib.resources import files, as_file  # py3.9+

def resolve_visus_home():
    # 1) user override, if set and truthy
    env = os.environ.get("VISUS_HOME")
    if env:
        try:
            return Path(env)
        except TypeError:
            pass  # env was somehow invalid

    # 2) default to a packaged resource dir (works when installed as a wheel)
    try:
        res = files("intake_nexgddp.resources")
        with as_file(res) as p:
            pkg_dir = Path(p)
        visus_home = pkg_dir  # or pkg_dir / "config" if that’s where your file is
    except Exception:
        # 3) last resort: library file’s parent
        visus_home = Path(__file__).resolve().parent

    os.environ["VISUS_HOME"] = str(visus_home)+'/resources'  # set for downstream code
    print("Setting VISUS_HOME =", visus_home)
    return visus_home


def load_visus_config_text():
    # If you just need the contents:
    cfg = files(f"{PKG}.resources").joinpath("visus.config")
    return cfg.read_text(encoding="utf-8")
