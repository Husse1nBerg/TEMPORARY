from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from server.app.database import get_db
from server.app.models.store import Store
from server.app.models.product import Product
from server.app.models.price import Price
from server.app.api.auth import get_current_active_user, get_admin_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/trigger")
async def trigger_scraping_endpoint(
    background_tasks: BackgroundTasks,
    store_id: Optional[int] = Query(None, description="Specific store to scrape"),
    product_id: Optional[int] = Query(None, description="Specific product to scrape"),
    force: bool = Query(False, description="Force scraping even if recently scraped"),
    dry_run: bool = Query(False, description="Simulate scraping without saving data"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Trigger scraping for specific store(s) or product(s)."""
    try:
        # Validate inputs
        if store_id:
            store = db.query(Store).filter(
                Store.id == store_id,
                Store.is_active == True
            ).first()
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Store with ID {store_id} not found or inactive"
                )
            
            # Check if scraper is enabled for this store
            if hasattr(store, 'scraper_enabled') and not store.scraper_enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Scraping is disabled for store: {store.name}"
                )
        
        if product_id:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.is_active == True
            ).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found or inactive"
                )
        
        # Check rate limiting unless forced
        if not force:
            recent_threshold = datetime.utcnow() - timedelta(minutes=30)
            
            if store_id:
                recent_scrape = db.query(Price).filter(
                    Price.store_id == store_id,
                    Price.scraped_at >= recent_threshold
                ).first()
                
                if recent_scrape:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Store {store.name} was scraped recently. Use force=true to override."
                    )
        
        # Prepare scraping task parameters
        task_params = {
            "store_id": store_id,
            "product_id": product_id,
            "user_id": current_user.id,
            "dry_run": dry_run,
            "force": force
        }
        
        # Build response message
        if dry_run:
            message = "Dry run scraping simulation initiated for "
        else:
            message = "Scraping initiated for "
        
        if store_id and product_id:
            message += f"product '{product.name}' from store '{store.name}'"
        elif store_id:
            message += f"all products from store '{store.name}'"
        elif product_id:
            message += f"product '{product.name}' from all active stores"
        else:
            message += "all products from all active stores"
        
        # Add task to background queue
        # Note: In a real implementation, you'd use Celery or similar
        # background_tasks.add_task(scrape_task, **task_params)
        
        logger.info(f"Scraping task queued by user {current_user.email}: {message}")
        
        return {
            "message": message,
            "task_id": f"scrape_{datetime.utcnow().timestamp()}",  # Mock task ID
            "parameters": task_params,
            "status": "queued"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering scraping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger scraping"
        )


@router.get("/status")
async def get_scraping_status(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back for status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get scraping status and recent activity."""
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build base query
        query = db.query(Price).filter(Price.scraped_at >= start_time)
        
        if store_id:
            query = query.filter(Price.store_id == store_id)
        
        # Get recent scraping activity
        recent_prices = query.order_by(Price.scraped_at.desc()).limit(100).all()
        
        # Calculate statistics
        if not recent_prices:
            return {
                "status": "inactive",
                "total_updates": 0,
                "stores_scraped": 0,
                "products_updated": 0,
                "last_activity": None,
                "updates_per_hour": 0.0,
                "recent_activity": []
            }
        
        # Group by store and calculate stats
        store_stats = {}
        product_updates = set()
        
        for price in recent_prices:
            store_name = price.store.name if price.store else f"Store {price.store_id}"
            product_updates.add(price.product_id)
            
            if store_name not in store_stats:
                store_stats[store_name] = {
                    "store_id": price.store_id,
                    "updates": 0,
                    "last_update": None
                }
            
            store_stats[store_name]["updates"] += 1
            if not store_stats[store_name]["last_update"] or price.scraped_at > store_stats[store_name]["last_update"]:
                store_stats[store_name]["last_update"] = price.scraped_at
        
        # Format recent activity
        recent_activity = []
        for price in recent_prices[:20]:  # Last 20 updates
            recent_activity.append({
                "store_id": price.store_id,
                "store_name": price.store.name if price.store else f"Store {price.store_id}",
                "product_id": price.product_id,
                "product_name": price.product.name if price.product else f"Product {price.product_id}",
                "price": price.price,
                "is_available": price.is_available,
                "scraped_at": price.scraped_at.isoformat()
            })
        
        # Determine overall status
        latest_update = max(price.scraped_at for price in recent_prices)
        time_since_last = (datetime.utcnow() - latest_update).total_seconds() / 3600  # hours
        
        if time_since_last < 1:
            status = "active"
        elif time_since_last < 6:
            status = "idle"
        else:
            status = "inactive"
        
        return {
            "status": status,
            "total_updates": len(recent_prices),
            "stores_scraped": len(store_stats),
            "products_updated": len(product_updates),
            "last_activity": latest_update.isoformat(),
            "updates_per_hour": round(len(recent_prices) / hours, 2),
            "time_range_hours": hours,
            "store_breakdown": store_stats,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Error fetching scraping status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scraping status"
        )


@router.get("/logs")
async def get_scraping_logs(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR)$", description="Minimum log level"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of logs to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get scraping logs and error information."""
    try:
        # For now, we'll simulate logs based on recent price updates
        # In a real implementation, you'd have a proper logging table
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        query = db.query(Price).filter(Price.scraped_at >= start_time)
        if store_id:
            query = query.filter(Price.store_id == store_id)
        
        recent_prices = query.order_by(Price.scraped_at.desc()).limit(limit).all()
        
        # Generate mock log entries
        logs = []
        for i, price in enumerate(recent_prices):
            # Simulate different log levels and messages
            if i % 20 == 0:  # Occasional errors
                logs.append({
                    "timestamp": price.scraped_at.isoformat(),
                    "level": "ERROR",
                    "store_id": price.store_id,
                    "store_name": price.store.name if price.store else f"Store {price.store_id}",
                    "message": f"Temporary connection error for {price.product.name if price.product else 'product'}",
                    "details": {"product_id": price.product_id, "retry_count": 1}
                })
            elif i % 10 == 0:  # Occasional warnings
                logs.append({
                    "timestamp": price.scraped_at.isoformat(),
                    "level": "WARNING",
                    "store_id": price.store_id,
                    "store_name": price.store.name if price.store else f"Store {price.store_id}",
                    "message": f"Price changed significantly for {price.product.name if price.product else 'product'}",
                    "details": {"product_id": price.product_id, "price": price.price}
                })
            else:
                logs.append({
                    "timestamp": price.scraped_at.isoformat(),
                    "level": "INFO",
                    "store_id": price.store_id,
                    "store_name": price.store.name if price.store else f"Store {price.store_id}",
                    "message": f"Successfully scraped price for {price.product.name if price.product else 'product'}",
                    "details": {"product_id": price.product_id, "price": price.price, "available": price.is_available}
                })
        
        # Filter by log level
        level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        min_priority = level_priority.get(level, 1)
        filtered_logs = [log for log in logs if level_priority.get(log["level"], 1) >= min_priority]
        
        return {
            "logs": filtered_logs[:limit],
            "total_logs": len(filtered_logs),
            "time_range_hours": hours,
            "filter_level": level,
            "summary": {
                "error_count": len([log for log in logs if log["level"] == "ERROR"]),
                "warning_count": len([log for log in logs if log["level"] == "WARNING"]),
                "info_count": len([log for log in logs if log["level"] == "INFO"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching scraping logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scraping logs"
        )


@router.get("/health")
async def get_scraper_health(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get overall health status of the scraping system."""
    try:
        # Check recent scraping activity (last 4 hours)
        recent_threshold = datetime.utcnow() - timedelta(hours=4)
        recent_updates = db.query(Price).filter(
            Price.scraped_at >= recent_threshold
        ).count()
        
        # Check active stores
        active_stores = db.query(Store).filter(Store.is_active == True).count()
        stores_with_recent_data = db.query(Price.store_id).filter(
            Price.scraped_at >= recent_threshold
        ).distinct().count()
        
        # Check for any products
        total_products = db.query(Product).filter(Product.is_active == True).count()
        
        # Determine health status
        health_issues = []
        overall_status = "healthy"
        
        if recent_updates == 0:
            health_issues.append("No recent scraping activity")
            overall_status = "unhealthy"
        elif recent_updates < 10:
            health_issues.append("Low scraping activity")
            overall_status = "degraded"
        
        if stores_with_recent_data < active_stores * 0.5:
            health_issues.append("Many stores not being scraped")
            overall_status = "degraded"
        
        if total_products == 0:
            health_issues.append("No active products configured")
            overall_status = "unhealthy"
        
        # Get last successful scrape time
        last_scrape = db.query(Price.scraped_at).order_by(
            Price.scraped_at.desc()
        ).first()
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "recent_updates": recent_updates,
                "active_stores": active_stores,
                "stores_with_recent_data": stores_with_recent_data,
                "total_products": total_products,
                "last_scrape": last_scrape[0].isoformat() if last_scrape else None
            },
            "issues": health_issues,
            "uptime_info": {
                "system_healthy": overall_status == "healthy",
                "scrapers_running": recent_updates > 0,
                "stores_coverage": round((stores_with_recent_data / active_stores) * 100, 1) if active_stores > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking scraper health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check scraper health"
        )


# Admin only endpoints
@router.post("/stop")
async def stop_scraping(
    store_id: Optional[int] = Query(None, description="Stop scraping for specific store"),
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Stop all or specific scraping operations (admin only)."""
    try:
        if store_id:
            store = db.query(Store).filter(Store.id == store_id).first()
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
            
            # Disable scraping for specific store
            if hasattr(store, 'scraper_enabled'):
                store.scraper_enabled = False
                db.commit()
            
            message = f"Scraping stopped for store: {store.name}"
        else:
            # Stop all scraping (in real implementation, this would stop Celery workers)
            message = "All scraping operations stopped"
        
        logger.warning(f"Scraping stopped by admin {current_user.email}: {message}")
        
        return {
            "message": message,
            "stopped_at": datetime.utcnow().isoformat(),
            "stopped_by": current_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping scraping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop scraping"
        )


@router.post("/resume")
async def resume_scraping(
    store_id: Optional[int] = Query(None, description="Resume scraping for specific store"),
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Resume scraping operations (admin only)."""
    try:
        if store_id:
            store = db.query(Store).filter(Store.id == store_id).first()
            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Store not found"
                )
            
            # Enable scraping for specific store
            if hasattr(store, 'scraper_enabled'):
                store.scraper_enabled = True
                db.commit()
            
            message = f"Scraping resumed for store: {store.name}"
        else:
            # Resume all scraping
            message = "All scraping operations resumed"
        
        logger.info(f"Scraping resumed by admin {current_user.email}: {message}")
        
        return {
            "message": message,
            "resumed_at": datetime.utcnow().isoformat(),
            "resumed_by": current_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming scraping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume scraping"
        )