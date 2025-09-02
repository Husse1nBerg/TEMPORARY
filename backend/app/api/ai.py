"""
AI API endpoints
Path: backend/app/api/ai.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth import get_current_user
from app.services.ai_service import ai_service
from app.services.price_service import PriceService

router = APIRouter()

@router.post("/analyze-trends")
async def analyze_price_trends(
    product_id: int = Query(...),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-powered price trend analysis"""
    
    # Get price history
    price_trends = PriceService.get_price_trends(db, product_id, days=days)
    
    if not price_trends:
        raise HTTPException(status_code=404, detail="No price history found")
    
    # Get AI analysis
    analysis = await ai_service.analyze_price_trends(price_trends)
    
    return {
        "product_id": product_id,
        "period_days": days,
        "analysis": analysis,
        "data_points": len(price_trends)
    }

@router.post("/predict-prices")
async def predict_future_prices(
    product_id: int = Query(...),
    store_id: Optional[int] = None,
    days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-powered price predictions"""
    
    # Get historical prices
    history = PriceService.get_price_trends(db, product_id, store_id, days=60)
    
    if len(history) < 7:
        raise HTTPException(status_code=400, detail="Insufficient historical data for prediction")
    
    # Extract prices for prediction
    historical_prices = [h['price'] for h in history]
    product_name = history[0].get('product_name', 'Product')
    
    # Get AI prediction
    prediction = await ai_service.predict_future_prices(
        product_name, 
        historical_prices, 
        days_ahead
    )
    
    return {
        "product_id": product_id,
        "store_id": store_id,
        "prediction": prediction,
        "historical_data_points": len(historical_prices)
    }

@router.post("/recommendations")
async def get_buying_recommendations(
    budget: Optional[float] = Query(None, ge=0),
    category: Optional[str] = None,
    prefer_organic: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-powered buying recommendations"""
    
    # Get current prices
    current_prices = PriceService.get_current_prices(
        db, 
        category=category, 
        is_available=True,
        limit=50
    )
    
    if not current_prices:
        raise HTTPException(status_code=404, detail="No products available")
    
    # Build user preferences
    user_preferences = {
        "budget": budget,
        "category": category,
        "prefer_organic": prefer_organic,
        "user_id": current_user.id
    }
    
    # Get AI recommendations
    recommendations = await ai_service.generate_buying_recommendations(
        db,
        user_preferences,
        current_prices
    )
    
    return {
        "recommendations": recommendations,
        "preferences": user_preferences,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/detect-anomaly")
async def detect_price_anomaly(
    price_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detect if a price is anomalous using AI"""
    
    from app.models.price import Price
    from app.models.price_history import PriceHistory
    
    # Get the price
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    
    # Get historical average
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    historical_prices = db.query(PriceHistory.price).filter(
        PriceHistory.product_id == price.product_id,
        PriceHistory.store_id == price.store_id,
        PriceHistory.recorded_at >= thirty_days_ago
    ).all()
    
    if not historical_prices:
        return {"is_anomaly": False, "reason": "No historical data available"}
    
    historical_avg = sum(p[0] for p in historical_prices) / len(historical_prices)
    
    # Get AI anomaly detection
    anomaly_analysis = await ai_service.detect_price_anomalies(
        price.price,
        historical_avg,
        price.product.name,
        price.store.name
    )
    
    return anomaly_analysis

@router.get("/market-insights")
async def get_market_insights(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI-generated market insights"""
    
    insights = await ai_service.generate_market_insights(db, category)
    
    return insights

@router.post("/optimize-shopping")
async def optimize_shopping_list(
    shopping_list: List[str],
    budget: float = Query(..., ge=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Optimize shopping list using AI"""
    
    if not shopping_list:
        raise HTTPException(status_code=400, detail="Shopping list cannot be empty")
    
    # Get current prices for all available products
    current_prices = PriceService.get_current_prices(
        db,
        is_available=True,
        limit=200
    )
    
    # Get AI optimization
    optimization = await ai_service.optimize_shopping_list(
        shopping_list,
        budget,
        current_prices
    )
    
    return optimization

@router.get("/chat")
async def chat_with_ai(
    message: str = Query(...),
    context: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Chat with AI assistant about prices and products"""
    
    if not ai_service.client:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        system_prompt = """You are a helpful assistant for CROPS Price Tracker, 
        specializing in Egyptian agricultural product prices and market analysis. 
        Provide concise, actionable advice about grocery shopping and price trends."""
        
        response = ai_service.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {message}" if context else message}
            ]
        )
        
        return {
            "response": response.content[0].text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")