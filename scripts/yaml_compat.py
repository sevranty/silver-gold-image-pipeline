from __future__ import annotations

import importlib.util
import sys
import sysconfig
from pathlib import Path


def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    for key in ("purelib", "platlib"):
        value = sysconfig.get_paths().get(key)
        if value:
            roots.append(Path(value))
    roots.extend(Path("/usr/lib").glob("python*/dist-packages"))
    roots.extend(Path("/usr/local/lib").glob("python*/dist-packages"))
    return roots


def load_yaml_module():
    for root in _candidate_roots():
        init = root / "yaml" / "__init__.py"
        if not init.is_file() or init.resolve() == Path(__file__).resolve():
            continue
        spec = importlib.util.spec_from_file_location("yaml", init, submodule_search_locations=[str(init.parent)])
        if spec is None or spec.loader is None:
            continue
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
            continue
        return module
    raise ModuleNotFoundError("PyYAML is required for validation; install PyYAML or use a Python environment with yaml available")


yaml = load_yaml_module()
