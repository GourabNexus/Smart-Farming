# agents/soil_agent.py
import streamlit as st

class SoilAgent:
    def __init__(self, farmer_input):
        self.location = farmer_input['location']
        self.land_type = farmer_input['land_type']
        self.area = farmer_input['area']
    
    def analyze_soil(self):
        """Analyze soil based on location and land type"""
        soil_data = {
            'type': self._determine_soil_type(),
            'ph': self._estimate_ph(),
            'nutrients': self._estimate_nutrients(),
            'moisture': self._estimate_moisture()
        }
        return soil_data
    
    def _determine_soil_type(self):
        """Map land type to soil composition"""
        soil_map = {
            'dry': 'sandy',
            'wet': 'clay',
            'upland': 'loamy',
            'lowland': 'silty'
        }
        return soil_map.get(self.land_type, 'loamy')
    
    def _estimate_ph(self):
        """Estimate pH based on location and soil type"""
        # In a real app, you'd use soil databases or APIs here
        return {
            'sandy': 6.2,
            'clay': 7.1,
            'loamy': 6.8,
            'silty': 6.5
        }.get(self._determine_soil_type(), 6.5)
    
    def _estimate_nutrients(self):
        """Estimate nutrient levels"""
        return {
            'N': round(0.5 if self.land_type == 'dry' else 0.8, 1),  # Nitrogen
            'P': round(0.6 if self.land_type == 'wet' else 0.7, 1),   # Phosphorus
            'K': round(0.7 if self.land_type == 'upland' else 0.6, 1) # Potassium
        }
    
    def _estimate_moisture(self):
        """Estimate soil moisture retention"""
        return {
            'sandy': 'low',
            'clay': 'high',
            'loamy': 'medium',
            'silty': 'medium-high'
        }.get(self._determine_soil_type(), 'medium')
    
    def recommend_crops(self, weather_forecast):
        """Recommend crops based on soil and weather"""
        soil_type = self._determine_soil_type()
        rainfall = weather_forecast.get('rainfall', 'moderate')
        temp = weather_forecast.get('temperature', 25)
        
        # Crop database (expand with your local knowledge)
        crop_db = {
            'sandy': {
                'low': ['Pearl millet', 'Sorghum', 'Groundnut'],
                'moderate': ['Maize', 'Sunflower', 'Watermelon'],
                'high': ['Sweet potato', 'Carrot', 'Cassava']
            },
            'clay': {
                'low': ['Wheat', 'Barley', 'Oats'],
                'moderate': ['Rice', 'Sugarcane', 'Soybean'],
                'high': ['Taro', 'Lettuce', 'Spinach']
            },
            'loamy': {
                'low': ['Chickpea', 'Lentil', 'Green gram'],
                'moderate': ['Tomato', 'Brinjal', 'Cabbage'],
                'high': ['Potato', 'Onion', 'Garlic']
            },
            'silty': {
                'low': ['Cotton', 'Sesame', 'Mustard'],
                'moderate': ['Wheat', 'Barley', 'Peas'],
                'high': ['Rice', 'Jute', 'Tobacco']
            }
        }
        
        # Temperature filtering
        base_crops = crop_db.get(soil_type, {}).get(rainfall, [])
        
        if temp < 15:
            return [c for c in base_crops if c in ['Wheat', 'Barley', 'Oats', 'Potato']]
        elif temp > 30:
            return [c for c in base_crops if c in ['Sorghum', 'Pearl millet', 'Groundnut', 'Cassava']]
        return base_crops
