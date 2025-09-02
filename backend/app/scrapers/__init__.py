"""
Scrapers module initialization
Path: backend/app/scrapers/__init__.py
"""

from app.scrapers.base_scraper import BaseScraper, ProductData
from app.scrapers.gourmet_scraper import GourmetScraper
from app.scrapers.rdna_scraper import RDNAScraper
from app.scrapers.metro_scraper import MetroScraper
from app.scrapers.spinneys_scraper import SpinneysScraper
from app.scrapers.rabbit_scraper import RabbitScraper
from app.scrapers.talabat_scraper import TalabatScraper
from app.scrapers.instashop_scraper import InstashopScraper
from app.scrapers.breadfast_scraper import BreadfastScraper

__all__ = [
    'BaseScraper',
    'ProductData',
    'GourmetScraper',
    'RDNAScraper',
    'MetroScraper',
    'SpinneysScraper',
    'RabbitScraper',
    'TalabatScraper',
    'InstashopScraper',
    'BreadfastScraper'
]