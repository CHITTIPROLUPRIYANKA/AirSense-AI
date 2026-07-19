import requests
import joblib
import pandas as pd

API_KEY = "65b4cdadec6e5c172a93cc5efe44ccbd"

city = "Hyderabad"

# Load ML model
model = joblib.load("models/aqi_model.pkl")

# Get coordinates
geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
geo_data = requests.get(geo_url).json()

lat = geo_data[0]["lat"]
lon = geo_data[0]["lon"]

# Get pollution data
air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
air_data = requests.get(air_url).json()

comp = air_data["list"][0]["components"]

# Create input for model
input_data = pd.DataFrame([{
    "PM2.5": comp["pm2_5"],
    "PM10": comp["pm10"],
    "NO2": comp["no2"],
    "CO": comp["co"],
    "SO2": comp["so2"],
    "O3": comp["o3"]
}])

# Predict AQI
predicted_aqi = model.predict(input_data)[0]

print(f"City: {city}")
print(f"Predicted AQI: {predicted_aqi:.2f}")