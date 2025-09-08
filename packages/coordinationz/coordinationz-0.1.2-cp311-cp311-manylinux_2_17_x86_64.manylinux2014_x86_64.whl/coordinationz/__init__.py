"""Python Package Template"""
from __future__ import annotations
__version__ = "0.1.2"

from .config import config, load_config, reload_config, save_config

from . import nullmodel, network, fastcosine
