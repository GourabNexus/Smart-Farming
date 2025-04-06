# agents/planner_agent.py
from datetime import datetime, timedelta
import random

class PlannerAgent:
    def __init__(self, yield_multiplier=1.2, risk_threshold=0.3):
        self.base_yield = {
            "wheat": 2000,  # kg/acre
            "rice": 2500,
            "millet": 1800,
            "maize": 3000,
            "default": 2000
        }
        self.yield_multiplier = yield_multiplier
        self.risk_threshold = risk_threshold

    def plan(self, farmer_input, weather_data, soil_report, expert_advice, market_data):
        """
        Generate comprehensive farming plan
        Returns:
            {
                "suggested_crop": str,
                "planting_strategy": str,
                "budget_plan": dict,
                "soil_management": list,
                "market_advice": str,
                "expert_tips": list,
                "risk_assessment": dict,
                "expected_yield": str
            }
        """
        # Validate inputs
        farmer_input = farmer_input or {}
        weather_data = weather_data or {}
        soil_report = soil_report or {}
        expert_advice = expert_advice or []
        market_data = market_data or {}

        # Core planning logic
        plan = {
            "suggested_crop": self._determine_crop(farmer_input, market_data),
            "planting_strategy": self._get_planting_schedule(weather_data),
            "budget_plan": self._create_budget_plan(farmer_input.get('budget', 'medium')),
            "soil_management": self._get_soil_recommendations(soil_report),
            "market_advice": self._generate_market_advice(market_data),
            "expert_tips": expert_advice,
            "risk_assessment": self._assess_risks(weather_data, soil_report),
            "expected_yield": self._calculate_yield(farmer_input, soil_report)
        }

        return plan

    def _determine_crop(self, farmer_input, market_data):
        """Determine optimal crop considering preferences and market"""
        preferred = farmer_input.get('preferred_crop')
        market_top = market_data.get('demand', {}).get('top_crop')
        soil_crops = farmer_input.get('recommended_crops', [])
        
        # Priority: 1. Market demand 2. Soil recommendation 3. Farmer preference
        if market_top and market_top in soil_crops:
            return market_top
        if soil_crops:
            return soil_crops[0]
        return preferred or market_top or "millet"

    def _get_planting_schedule(self, weather_data):
        """Calculate optimal planting window"""
        today = datetime.now()
        rainfall = weather_data.get('rainfall', 'moderate').lower()
        
        if rainfall in ['heavy', 'very heavy']:
            return {
                "window": "15-30 days after rain subsides",
                "recommended_date": (today + timedelta(days=15)).strftime("%d-%b-%Y")
            }
        
        return {
            "window": "Immediate planting recommended",
            "recommended_date": today.strftime("%d-%b-%Y")
        }

    def _create_budget_plan(self, budget_level):
        """Generate budget-specific input plan"""
        plans = {
            "low": {
                "fertilizer": "Organic manure only",
                "pesticides": "Neem oil biopesticides",
                "irrigation": "Rain-fed",
                "equipment": "Manual tools"
            },
            "medium": {
                "fertilizer": "50% organic + 50% chemical",
                "pesticides": "Combination approach",
                "irrigation": "Drip irrigation",
                "equipment": "Basic machinery"
            },
            "high": {
                "fertilizer": "Precision farming inputs",
                "pesticides": "Integrated pest management",
                "irrigation": "Automated systems",
                "equipment": "Full mechanization"
            }
        }
        return plans.get(budget_level.lower(), plans['medium'])

    def _get_soil_recommendations(self, soil_report):
        """Generate soil improvement recommendations"""
        recs = []
        nutrients = soil_report.get('nutrients', {})
        
        if nutrients.get('N', 0) < 0.6:
            recs.append("Apply nitrogen-rich fertilizers (Urea)")
        if nutrients.get('P', 0) < 0.4:
            recs.append("Add phosphate fertilizers (DAP)")
        if nutrients.get('K', 0) < 0.5:
            recs.append("Use potash fertilizers (MOP)")
            
        if soil_report.get('ph', 7) < 6:
            recs.append("Apply lime to reduce acidity")
        elif soil_report.get('ph', 7) > 7.5:
            recs.append("Add sulfur to reduce alkalinity")
            
        return recs or ["Soil conditions optimal - maintain current practices"]

    def _generate_market_advice(self, market_data):
        """Generate market-oriented advice"""
        trend = market_data.get('demand', {}).get('trend', 'stable')
        price = market_data.get('prices', [{}])[0].get('modal_price', 0)
        
        advice = []
        if trend == 'increasing':
            advice.append("Consider holding stock for better prices")
        elif trend == 'decreasing':
            advice.append("Recommend immediate sale after harvest")
            
        if price > 5000:
            advice.append("High current prices - good time to sell")
        return " ".join(advice) or "Market conditions stable"

    def _assess_risks(self, weather_data, soil_report):
        """Evaluate potential risks"""
        risks = {}
        
        # Weather risks
        if weather_data.get('rainfall') in ['heavy', 'very heavy']:
            risks['flooding'] = {
                "probability": 0.7,
                "mitigation": "Ensure proper drainage systems"
            }
            
        if weather_data.get('temperature', 0) > 35:
            risks['heat_stress'] = {
                "probability": 0.6,
                "mitigation": "Install shade nets and increase irrigation"
            }
            
        # Soil risks
        if soil_report.get('moisture') == 'low':
            risks['drought'] = {
                "probability": 0.65,
                "mitigation": "Implement water conservation measures"
            }
            
        return risks or {"status": "Low risk conditions"}

    def _calculate_yield(self, farmer_input, soil_report):
        """Estimate expected yield"""
        base = self.base_yield.get(
            farmer_input.get('preferred_crop', 'default'),
            self.base_yield['default']
        )
        
        # Soil quality multiplier
        soil_quality = sum([
            soil_report.get('nutrients', {}).get('N', 0),
            soil_report.get('nutrients', {}).get('P', 0),
            soil_report.get('nutrients', {}).get('K', 0)
        ]) / 3
        
        area = farmer_input.get('area', 1)
        return f"{round(base * area * soil_quality * self.yield_multiplier, 2)} kg"
