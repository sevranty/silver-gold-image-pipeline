from __future__ import annotations

import importlib
import importlib.util
import site
import sys
import sysconfig
from pathlib import Path


def _candidate_roots() -> list[Path]:
    values: list[str] = []
    try:
        values.extend(site.getsitepackages())
    except AttributeError:
        pass
    user_site = site.getusersitepackages()
    if isinstance(user_site, str):
        values.append(user_site)
    for key in ("purelib", "platlib"):
        value = sysconfig.get_paths().get(key)
        if value:
            values.append(value)
    values.extend(str(path) for path in Path("/usr/lib").glob("python*/dist-packages"))
    values.extend(str(path) for path in Path("/usr/local/lib").glob("python*/dist-packages"))

    roots: list[Path] = []
    seen: set[Path] = set()
    for value in values:
        root = Path(value).expanduser().resolve()
        if root not in seen:
            seen.add(root)
            roots.append(root)
    return roots


def _load_from_root(root: Path):
    init = root / "yaml" / "__init__.py"
    if not init.is_file():
        return None
    spec = importlib.util.spec_from_file_location("yaml", init, submodule_search_locations=[str(init.parent)])
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get("yaml")
    sys.modules["yaml"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is not None:
            sys.modules["yaml"] = previous
        else:
            sys.modules.pop("yaml", None)
        return None
    return module


def load_yaml_module():
    try:
        return importlib.import_module("yaml")
    except ModuleNotFoundError as exc:
        if exc.name != "yaml":
            raise
    for root in _candidate_roots():
        module = _load_from_root(root)
        if module is not None:
            return module
    raise ModuleNotFoundError("PyYAML is required for validation; install PyYAML or use a Python environment with yaml available")


yaml = load_yaml_module()
