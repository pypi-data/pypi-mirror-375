import os
from pathlib import Path

def ensure_visus_env() -> Path:

    env = os.environ.get("VISUS_HOME")
    if env:
        p = Path(env)
        cfg = p / "visus.config"
        if cfg.is_file() and cfg.stat().st_size > 0:
            return p
        raise RuntimeError(f"VISUS_HOME={p} does not contain a non-empty visus.config")

    # 2) Package resources (the path you were setting manually from the client)
    pkg_resources = Path(__file__).resolve().parent / "resources"
    cfg = pkg_resources / "visus.config"
    if cfg.is_file() and cfg.stat().st_size > 0:
        os.environ["VISUS_HOME"] = str(pkg_resources)
        return pkg_resources

    # 3) Hard fail to surface packaging mistakes immediately
    raise RuntimeError(
        "visus.config not found in package resources. Expected at:\n"
        f"  {pkg_resources}/visus.config\n"
        "Make sure 'intake_nexgddp/resources/visus.config' exists in the source tree "
        "and is included via package_data (and MANIFEST.in for sdist)."
    )
