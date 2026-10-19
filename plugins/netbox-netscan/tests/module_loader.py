"""Load pure scanner modules without importing the Django plugin entry point."""
import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).parents[1] / "netbox_netscan"


def load_module(name, relative_path):
    for package in ("netbox_netscan", "netbox_netscan.scanning"):
        if package not in sys.modules:
            module = types.ModuleType(package)
            module.__path__ = []
            sys.modules[package] = module
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


parser = load_module("netbox_netscan.scanning.parser", "scanning/parser.py")
risk = load_module("netbox_netscan.scanning.risk", "scanning/risk.py")
scanner = load_module("netbox_netscan.scanning.scanner", "scanning/scanner.py")

