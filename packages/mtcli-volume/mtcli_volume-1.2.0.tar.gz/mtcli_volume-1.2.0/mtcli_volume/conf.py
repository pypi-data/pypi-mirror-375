import os
from mtcli.conf import config


SYMBOL = os.getenv("SYMBOL", config["DEFAULT"].get("symbol", fallback="WIN$N"))
DIGITOS = os.getenv("DIGITOS", config["DEFAULT"].getint("digitos", fallback=0))
PERIODS = os.getenv("PERIODS", config["DEFAULT"].getint("periods", fallback=566))
STEP = os.getenv("STEP", config["DEFAULT"].getfloat("step", fallback=100))
