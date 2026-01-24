from .sqlite import SqlitePocket
from .tinydb import TinyDbPocket

POCKET_CLASSES = {"tinydb": TinyDbPocket, "sqlite": SqlitePocket}
