from fastapi import APIRouter

# Import all API route modules
from . import auth, products, stores, prices, scraper

# Main API router
api_router = APIRouter()

# Include all sub-routers with their prefixes and tags
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(stores.router, prefix="/stores", tags=["Stores"])
api_router.include_router(prices.router, prefix="/prices", tags=["Prices"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["Scraping"])

__all__ = ["api_router"]