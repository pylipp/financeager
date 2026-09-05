from .sqlite import SqlitePocket

POCKET_CLASSES = {"sqlite": SqlitePocket}
try:
    from .tinydb import TinyDbPocket

    POCKET_CLASSES["tinydb"] = TinyDbPocket
except ModuleNotFoundError:
    pass
