import requests
import pandas as pd
from datetime import datetime, timedelta

class MarketAgent:
    def __init__(self, location):
        self.location = location
        self.api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
        self.base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    def _fetch_agmarknet_data(self, commodity, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        params = {
            "api-key": self.api_key,
            "format": "json",
            "filters[commodity]": commodity.title(),
            "filters[state]": self.location.title(),
            "limit": 1000
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            records = response.json().get("records", [])
            df = pd.DataFrame(records)
            if df.empty:
                return None

            df = df[df["arrival_date"].between(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))]
            df["Modal Price"] = pd.to_numeric(df["modal_price"], errors="coerce")
            df["Min Price"] = pd.to_numeric(df["min_price"], errors="coerce")
            df["Max Price"] = pd.to_numeric(df["max_price"], errors="coerce")
            df["Date"] = pd.to_datetime(df["arrival_date"])
            df["Market"] = df["market"]
            df["Unit"] = "Quintal"

            return df.sort_values("Date", ascending=False)
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def get_crop_demand(self, crop=None):
        if crop:
            data = self._fetch_agmarknet_data(crop)
            if data is not None and not data.empty:
                latest = data.iloc[0]
                return {
                    "crop": crop,
                    "demand": "High" if float(latest['Modal Price']) > 5000 else "Medium",
                    "trend": self._analyze_trend(data),
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }

        return {
            "top_crop": "millet",
            "market_price": "₹30/kg",
            "trend": "stable",
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }

    def get_market_prices(self, commodity):
        data = self._fetch_agmarknet_data(commodity, days=1)
        if data is not None and not data.empty:
            return [{
                "mandi": row['Market'],
                "min_price": row['Min Price'],
                "modal_price": row['Modal Price'],
                "max_price": row['Max Price'],
                "unit": "Quintal"
            } for _, row in data.iterrows()]
        return [{
            "mandi": f"{self.location} Main Market",
            "min_price": 1800,
            "modal_price": 2200,
            "max_price": 2600,
            "unit": "Quintal"
        }]

    def get_price_trends(self, commodity):
        data = self._fetch_agmarknet_data(commodity, days=30)
        if data is not None and not data.empty:
            return data[['Date', 'Market', 'Modal Price', 'Unit']].rename(columns={
                'Date': 'date',
                'Market': 'mandi',
                'Modal Price': 'modal_price',
                'Unit': 'unit'
            })
        return pd.DataFrame({
            "date": [datetime.now().strftime("%Y-%m-%d")],
            "mandi": [f"{self.location} Mandi"],
            "modal_price": [2200],
            "unit": ["Quintal"]
        })

    def _analyze_trend(self, df):
        if df is None or len(df) < 2:
            return "stable"
        prices = df['Modal Price'].astype(float)
        if prices.iloc[-1] > prices.mean() * 1.1:
            return "increasing"
        return "decreasing" if prices.iloc[-1] < prices.mean() * 0.9 else "stable"