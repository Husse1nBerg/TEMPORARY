"""
CROPS Price Tracker Backend Application
Path: backend/app/__init__.py
"""

__version__ = "1.0.0"
__author__ = "CROPS Egypt"

# Make sure all modules are importable
from . import models
from . import schemas
from . import api
from . import scrapers
from . import services
from . import tasks
from . import utils