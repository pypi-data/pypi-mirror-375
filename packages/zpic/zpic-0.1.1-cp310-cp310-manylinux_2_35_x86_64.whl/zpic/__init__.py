# this script loads the compiled binaries into the module namespace dynamically

from pathlib import Path
from sys import path

lib_dir = Path(__file__).parent
path.append(str(lib_dir))

modules = []

# default plugins
for bin in lib_dir.iterdir():
    name = bin.name.split('.')[0]
    if name.startswith('__'):
        continue
    try:
        globals()[name] = __import__(name)
        modules.append(name)
    except ImportError:
        globals()[name] = None
    