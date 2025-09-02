
import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import anthropic
from sqlalchemy.orm import Session
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI-powered service for intelligent price analysis and predictions"""
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("Anthropic API key not found. AI features will be limited.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    async def analyze_price_trends(self, price_history: List[Dict]) -> Dict[str, Any]:
        """
        Use AI to analyze price trends and provide insights
        """
        if not self.client:
            return self._fallback_analysis(price_history)
        
        try:
            # Prepare data for AI analysis
            price_data = json.dumps(price_history, default=str)
            
            prompt = f"""Analyze the following price history data for agricultural products in Egypt:

{price_data}

Provide a comprehensive analysis including:
1. Overall price trend (increasing/decreasing/stable)
2. Volatility assessment
3. Seasonal patterns if any
4. Price prediction for next 7 days
5. Recommended buying strategy
6. Risk assessment

Format your response as a JSON object with these keys: trend, volatility, seasonal_pattern, prediction, strategy, risk_level, insights"""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.content[0].text)
            return ai_analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(price_history)
    
    async def predict_future_prices(
        self, 
        product_name: str, 
        historical_prices: List[float],
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        AI-powered price prediction
        """
        if not self.client:
            return self._simple_prediction(historical_prices, days_ahead)
        
        try:
            prompt = f"""Based on the historical prices for {product_name}:
{historical_prices}

Predict the likely prices for the next {days_ahead} days. Consider:
1. Recent trend direction and strength
2. Price volatility patterns
3. Typical market cycles for agricultural products
4. Seasonal factors

Provide predictions as a JSON object with:
- predicted_prices: array of {days_ahead} price predictions
- confidence: confidence level (low/medium/high)
- factors: key factors influencing the prediction
- risk: potential risks to the prediction"""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.4,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            prediction = json.loads(response.content[0].text)
            return prediction
            
        except Exception as e:
            logger.error(f"Price prediction failed: {e}")
            return self._simple_prediction(historical_prices, days_ahead)
    
    async def generate_buying_recommendations(
        self, 
        db: Session,
        user_preferences: Dict,
        current_prices: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered buying recommendations
        """
        if not self.client:
            return self._simple_recommendations(current_prices)
        
        try:
            prompt = f"""Given the current agricultural product prices in Egyptian markets:
{json.dumps(current_prices, default=str)}

And user preferences:
{json.dumps(user_preferences)}

Generate smart buying recommendations. Consider:
1. Best value products (price per kg)
2. Products with recent price drops
3. Stock availability across stores
4. Organic vs regular trade-offs
5. Bulk buying opportunities

Provide recommendations as a JSON array, each with:
- product_name
- store_name
- reason: why this is recommended
- urgency: low/medium/high
- potential_savings
- alternative_options"""

            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            recommendations = json.loads(response.content[0].text)
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return self._simple_recommendations(current_prices)
    
    async def detect_price_anomalies(
        self, 
        current_price: float,
        historical_avg: float,
        product_name: str,
        store_name: str
    ) -> Dict[str, Any]:
        """
        Detect unusual price changes using AI
        """
        if not self.client:
            return self._simple_anomaly_detection(current_price, historical_avg)
        
        try:
            deviation = ((current_price - historical_avg) / historical_avg) * 100
            
            prompt = f"""Analyze this price situation:
Product: {product_name}
Store: {store_name}
Current Price: {current_price} EGP
Historical Average: {historical_avg} EGP
Deviation: {deviation:.2f}%

Determine if this is:
1. A normal price fluctuation
2. A potential pricing error
3. A market anomaly requiring attention
4. A seasonal/expected change

Provide analysis as JSON with:
- is_anomaly: boolean
- severity: none/low/medium/high
- likely_cause: string explaining the likely reason
- recommended_action: what the user should do
- confidence: confidence in this assessment"""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            anomaly_analysis = json.loads(response.content[0].text)
            return anomaly_analysis
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return self._simple_anomaly_detection(current_price, historical_avg)
    
    async def generate_market_insights(
        self,
        db: Session,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered market insights and reports
        """
        if not self.client:
            return {"insights": "AI insights unavailable", "summary": "Please configure API key"}
        
        try:
            # Get recent price data from database
            from app.models.price import Price
            from app.models.product import Product
            
            query = db.query(Price).join(Product)
            if category:
                query = query.filter(Product.category == category)
            
            recent_prices = query.order_by(Price.scraped_at.desc()).limit(100).all()
            
            price_data = [
                {
                    "product": p.product.name,
                    "store": p.store.name,
                    "price": p.price,
                    "price_per_kg": p.price_per_kg,
                    "is_available": p.is_available,
                    "date": p.scraped_at.isoformat()
                }
                for p in recent_prices
            ]
            
            prompt = f"""Analyze this Egyptian agricultural market data and generate professional insights:

{json.dumps(price_data, default=str)}

Provide a comprehensive market analysis including:
1. Executive Summary (2-3 sentences)
2. Key Market Trends
3. Price Leaders and Laggards
4. Supply Observations
5. Strategic Recommendations for buyers
6. Market Outlook (next 30 days)

Format as JSON with keys: executive_summary, trends, price_leaders, price_laggards, supply_status, recommendations, outlook"""

            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.6,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            insights = json.loads(response.content[0].text)
            insights['generated_at'] = datetime.utcnow().isoformat()
            return insights
            
        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            return {
                "executive_summary": "Unable to generate AI insights",
                "error": str(e)
            }
    
    async def optimize_shopping_list(
        self,
        shopping_list: List[str],
        budget: float,
        current_prices: List[Dict]
    ) -> Dict[str, Any]:
        """
        AI-powered shopping list optimization
        """
        if not self.client:
            return {"optimized_list": shopping_list, "total_cost": 0}
        
        try:
            prompt = f"""Optimize this shopping list for Egyptian grocery stores:

Shopping List: {shopping_list}
Budget: {budget} EGP
Available Products and Prices: {json.dumps(current_prices, default=str)}

Provide an optimized shopping plan that:
1. Stays within budget
2. Suggests best stores for each item
3. Identifies substitutions for expensive items
4. Calculates total savings
5. Suggests bulk buying where economical

Return as JSON with:
- optimized_list: array of items with store and price
- total_cost: total amount
- savings: amount saved through optimization
- substitutions: suggested replacements
- bulk_suggestions: items worth buying in bulk
- store_route: optimal store visiting order"""

            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.4,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            optimization = json.loads(response.content[0].text)
            return optimization
            
        except Exception as e:
            logger.error(f"Shopping list optimization failed: {e}")
            return {"optimized_list": shopping_list, "total_cost": 0, "error": str(e)}
    
    # Fallback methods for when AI is unavailable
    def _fallback_analysis(self, price_history: List[Dict]) -> Dict[str, Any]:
        """Simple statistical analysis when AI is unavailable"""
        if not price_history:
            return {"error": "No data available"}
        
        prices = [p.get('price', 0) for p in price_history]
        
        return {
            "trend": "increasing" if prices[-1] > prices[0] else "decreasing",
            "volatility": "moderate",
            "seasonal_pattern": "unknown",
            "prediction": "Analysis requires AI",
            "strategy": "Monitor prices daily",
            "risk_level": "medium",
            "insights": "Enable AI for detailed insights"
        }
    
    def _simple_prediction(self, historical_prices: List[float], days_ahead: int) -> Dict:
        """Simple linear prediction when AI is unavailable"""
        if len(historical_prices) < 2:
            return {"predicted_prices": [historical_prices[-1]] * days_ahead}
        
        # Simple moving average
        recent_avg = np.mean(historical_prices[-7:])
        trend = (historical_prices[-1] - historical_prices[-7]) / 7 if len(historical_prices) >= 7 else 0
        
        predictions = []
        for i in range(days_ahead):
            predictions.append(round(recent_avg + (trend * i), 2))
        
        return {
            "predicted_prices": predictions,
            "confidence": "low",
            "factors": ["Simple statistical projection"],
            "risk": "High uncertainty without AI analysis"
        }
    
    def _simple_recommendations(self, current_prices: List[Dict]) -> List[Dict]:
        """Basic recommendations when AI is unavailable"""
        sorted_prices = sorted(current_prices, key=lambda x: x.get('price_per_kg', float('inf')))
        
        recommendations = []
        for price in sorted_prices[:5]:
            recommendations.append({
                "product_name": price.get('product_name'),
                "store_name": price.get('store_name'),
                "reason": "Low price per kg",
                "urgency": "medium",
                "potential_savings": "Unknown",
                "alternative_options": []
            })
        
        return recommendations
    
    def _simple_anomaly_detection(self, current_price: float, historical_avg: float) -> Dict:
        """Basic anomaly detection when AI is unavailable"""
        if historical_avg == 0:
            return {"is_anomaly": False, "severity": "none"}
        
        deviation = abs((current_price - historical_avg) / historical_avg)
        
        return {
            "is_anomaly": deviation > 0.3,
            "severity": "high" if deviation > 0.5 else "medium" if deviation > 0.3 else "low",
            "likely_cause": "Price variation detected",
            "recommended_action": "Monitor closely",
            "confidence": "low"
        }

# Create singleton instance
ai_service = AIService()