import requests

API_KEY = "65b4cdadec6e5c172a93cc5efe44ccbd"

city = "Hyderabad"

# Get coordinates
geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
geo_data = requests.get(geo_url).json()

lat = geo_data[0]["lat"]
lon = geo_data[0]["lon"]

# Get air pollution data
air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

air_data = requests.get(air_url).json()

print(air_data)