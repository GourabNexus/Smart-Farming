import streamlit as st
import pandas as pd
from datetime import datetime
from agents.farmer_agent import FarmerAgent
from agents.weather_agent import WeatherAgent
from agents.soil_agent import SoilAgent
from agents.expert_agent import ExpertAgent
from agents.market_agent import MarketAgent
from agents.planner_agent import PlannerAgent

st.set_page_config(page_title="Smart Farming Assistant", page_icon="🌾", layout="centered")
st.title("🌱 Smart Farming Recommendation System")
st.markdown("Get personalized crop and farming recommendations based on your land, weather, soil, and market conditions.")

# Sidebar Weather Input
st.sidebar.header("🌤 Current Weather")
location_weather = st.sidebar.text_input("Check weather for location:", "Karnataka")

if location_weather:
    try:
        weather_agent = WeatherAgent(location_weather)
        current_weather = weather_agent.get_forecast()
        
        if 'error' in current_weather:
            st.sidebar.error(f"Weather data error: {current_weather['error']}")
        else:
            st.sidebar.subheader(f"Weather in {location_weather}")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("Temperature", f"{current_weather['temperature']}°C")
                st.metric("Humidity", f"{current_weather['humidity']}%")
            with col2:
                st.metric("Rainfall", str(current_weather['rainfall']).capitalize())
                st.metric("Wind", f"{current_weather['wind_speed']} km/h")
            st.sidebar.caption(f"Conditions: {current_weather['description'].capitalize()}")
    except Exception as e:
        st.sidebar.error(f"Failed to get weather data: {str(e)}")

# Main Form
with st.form("farmer_form"):
    st.subheader("👨‍🌾 Farmer Input")
    location = st.text_input("Your Location (e.g., Karnataka)", "Karnataka")
    land_type = st.selectbox("Land Type", ["dry", "wet", "upland", "lowland"])
    area = st.number_input("Area of Land (in acres)", min_value=0.1, value=2.0)
    budget = st.selectbox("Budget", ["low", "medium", "high"])
    preferred_crop = st.text_input("Preferred Crop (optional)", "")
    submitted = st.form_submit_button("Get Recommendation 🌾")

if submitted:
    farmer_input = {
        "location": location,
        "land_type": land_type,
        "area": area,
        "budget": budget,
        "preferred_crop": preferred_crop if preferred_crop else None
    }

    farmer = FarmerAgent(farmer_input)
    weather = WeatherAgent(location)
    soil = SoilAgent(farmer_input)

    with st.spinner("🌦 Fetching weather data..."):
        forecast = weather.get_forecast()
        forecast.setdefault('rainfall', 'moderate')
        forecast.setdefault('temperature', 25)
        forecast.setdefault('humidity', 60)
        forecast.setdefault('wind_speed', 10)
        forecast.setdefault('description', 'clear sky')

    with st.spinner("🌱 Analyzing soil conditions..."):
        soil_report = soil.analyze_soil()
        soil_report.setdefault('type', 'loamy')
        soil_report.setdefault('ph', 6.5)
        soil_report.setdefault('moisture', 'medium')
        soil_report.setdefault('nutrients', {'N': 0.5, 'P': 0.5, 'K': 0.5})

    # Tabs for output
    tab1, tab2, tab3 = st.tabs(["Weather Report", "Soil Analysis", "Crop Recommendations"])

    with tab1:
        st.markdown("### 🌦 Detailed Weather Analysis")
        if 'error' in forecast:
            st.warning(f"Couldn't fetch weather data: {forecast['error']}")
        else:
            cols = st.columns(4)
            cols[0].metric("Temperature", f"{forecast['temperature']}°C")
            cols[1].metric("Rainfall", str(forecast['rainfall']).capitalize())
            cols[2].metric("Humidity", f"{forecast['humidity']}%")
            cols[3].metric("Wind Speed", f"{forecast['wind_speed']} km/h")
            st.caption(f"Current conditions: {forecast['description'].capitalize()}")

    with tab2:
        st.subheader("🌱 Soil Analysis Report")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Soil Type", soil_report['type'].capitalize())
            st.metric("pH Level", soil_report['ph'])
        with col2:
            st.metric("Moisture Retention", soil_report['moisture'].capitalize())
            nutrients = soil_report['nutrients']
            st.metric("Primary Nutrients", f"N:{nutrients['N']} P:{nutrients['P']} K:{nutrients['K']}")

        st.progress(min(nutrients['N'] + 0.2, 1.0), text=f"Nitrogen: {nutrients['N']}")
        st.progress(min(nutrients['P'] + 0.2, 1.0), text=f"Phosphorus: {nutrients['P']}")
        st.progress(min(nutrients['K'] + 0.2, 1.0), text=f"Potassium: {nutrients['K']}")

    with tab3:
        recommended_crops = soil.recommend_crops(forecast) or []
        st.subheader("🌾 Top Recommended Crops")

        if preferred_crop and preferred_crop in recommended_crops:
            st.success(f"Your preferred crop ({preferred_crop}) is suitable!")

        for i, crop in enumerate(recommended_crops[:5], 1):
            with st.expander(f"🥕 {crop}"):
                st.write("- Ideal for {} soil".format(soil_report['type']))
                st.write("- Thrives in {} rainfall conditions".format(forecast['rainfall']))
                st.write("- Grows well at {}°C".format(forecast['temperature']))

        if preferred_crop and preferred_crop not in recommended_crops:
            st.warning(f"Note: {preferred_crop} may not be ideal for current conditions")

    with st.spinner("📈 Analyzing market trends..."):
        try:
            market = MarketAgent(location)
            top_crop = recommended_crops[0] if recommended_crops else (preferred_crop or "wheat")
            market_data = market.get_market_prices(top_crop)
            price_trends = market.get_price_trends(top_crop)
            demand_data = market.get_crop_demand(top_crop)
        except Exception as e:
            st.error(f"Market service error: {str(e)}")
            market_data = []
            price_trends = pd.DataFrame()
            demand_data = {}

    st.markdown("---")
    st.subheader("📊 Market Intelligence")

    if isinstance(market_data, list) and market_data:
        with st.expander(f"💰 Current {top_crop.title()} Prices", expanded=True):
            cols = st.columns(3)
            cols[0].metric("Min Price", f"₹{market_data[0].get('min_price', 'N/A')}/{market_data[0].get('unit', 'Quintal')}")
            cols[1].metric("Modal Price", f"₹{market_data[0].get('modal_price', 'N/A')}/{market_data[0].get('unit', 'Quintal')}")
            cols[2].metric("Max Price", f"₹{market_data[0].get('max_price', 'N/A')}/{market_data[0].get('unit', 'Quintal')}")
            st.caption(f"Data from {market_data[0].get('mandi', 'local')} market")

        with st.expander("📈 Price Trends (Last 30 Days)"):
            if isinstance(price_trends, pd.DataFrame) and not price_trends.empty:
                st.line_chart(price_trends.set_index("date")["modal_price"], color="#27ae60")
                st.dataframe(
                    price_trends[["date", "mandi", "modal_price", "unit"]],
                    hide_index=True,
                    column_config={
                        "date": "Date",
                        "mandi": "Market",
                        "modal_price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
                        "unit": "Unit"
                    }
                )
            else:
                st.warning("No trend data available")

        with st.expander("📊 Demand Analysis"):
            if isinstance(demand_data, dict) and 'error' not in demand_data:
                cols = st.columns(2)
                cols[0].metric("Demand Level", demand_data.get('demand', 'N/A'))
                cols[1].metric("Market Trend", demand_data.get('trend', 'N/A'))
                st.caption(f"Last updated: {demand_data.get('last_updated', 'Unknown')}")
    else:
        st.warning("Market data service is currently unavailable")

    # Final Recommendation
with st.spinner("✨ Generating final plan..."):
    try:
        expert = ExpertAgent()
        expert_advice = expert.suggest_practices(soil_report, forecast)
        
        # Include recommended crops in input for planner
        farmer_input['recommended_crops'] = recommended_crops
        
        planner = PlannerAgent()
        recommendation = planner.plan(
            farmer_input, 
            forecast, 
            soil_report, 
            expert_advice,
            {
                'prices': market_data,
                'trends': price_trends,
                'demand': demand_data
            }
        )
        
        st.markdown("---")
        st.success(f"✅ Recommended Crop: {recommendation['suggested_crop'].title()}")
        
        with st.expander("🌾 View Detailed Farming Plan", expanded=True):
            planting = recommendation.get("planting_strategy", {})
            st.write(f"*Planting Window*: {planting.get('window', 'N/A')}")
            st.write(f"*Recommended Date*: {planting.get('recommended_date', 'N/A')}")
            st.write(f"*Expected Yield*: {recommendation.get('expected_yield', 'N/A')}")
            
            st.write("### 💰 Budget Plan")
            st.json(recommendation.get("budget_plan", {}))
            
            st.write("### 🧪 Soil Management Recommendations")
            for item in recommendation.get("soil_management", []):
                st.markdown(f"- {item}")
            
            st.write("### 📈 Market Advice")
            st.write(recommendation.get("market_advice", "N/A"))
            
            st.write("### 🧠 Expert Tips")
            for tip in recommendation.get("expert_tips", []):
                st.markdown(f"- {tip}")
            
            st.write("### ⚠ Risk Assessment")
            risks = recommendation.get("risk_assessment", {})
            if isinstance(risks, dict) and risks:
                for risk, details in risks.items():
                    st.markdown(f"- *{risk.title()}*: Probability {details.get('probability', 'N/A')} — {details.get('mitigation', 'N/A')}")
            else:
                st.markdown("No major risks detected.")

    except Exception as e:
        st.error(f"Failed to generate final recommendation: {str(e)}")