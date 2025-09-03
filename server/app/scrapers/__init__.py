from .base_scraper import BaseScraper, ScrapedProduct, ScraperResult
from .gourmet_scraper import GourmetScraper
from .rdna_scraper import RDNAScraper
from .metro_scraper import MetroScraper
from .spinneys_scraper import SpinneysScraper
from .rabbit_scraper import RabbitScraper
from .talabat_scraper import TalabatScraper
from .instashop_scraper import InstashopScraper
from .breadfast_scraper import BreadfastScraper

# Scraper registry for dynamic instantiation
SCRAPER_REGISTRY = {
    'GourmetScraper': GourmetScraper,
    'RDNAScraper': RDNAScraper,
    'MetroScraper': MetroScraper,
    'SpinneysScraper': SpinneysScraper,
    'RabbitScraper': RabbitScraper,
    'TalabatScraper': TalabatScraper,
    'InstashopScraper': InstashopScraper,
    'BreadfastScraper': BreadfastScraper,
}

__all__ = [
    'BaseScraper', 'ScrapedProduct', 'ScraperResult', 'SCRAPER_REGISTRY',
    'GourmetScraper', 'RDNAScraper', 'MetroScraper', 'SpinneysScraper',
    'RabbitScraper', 'TalabatScraper', 'InstashopScraper', 'BreadfastScraper'
]


def get_scraper(scraper_name: str) -> type:
    """Get scraper class by name."""
    if scraper_name not in SCRAPER_REGISTRY:
        raise ValueError(f"Unknown scraper: {scraper_name}")
    return SCRAPER_REGISTRY[scraper_name]