from flask import Flask, render_template, request, redirect
import requests
import joblib
import pandas as pd
import os
import traceback

app = Flask(__name__)

# Load models
model = joblib.load("models/aqi_model.pkl")
forecast_model = joblib.load("models/forecast_model.pkl")


OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
recent_cities = [] 

latest_data = {
    "city": None,
    "prediction": None,
    "category": None,
    "pollutants": None,
    "forecast": None
}



def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"
    

def get_city_aqi(city_name):
    try:
        geo_url = (
            f"http://api.openweathermap.org/geo/1.0/direct"
            f"?q={city_name}&limit=1&appid={OPENWEATHER_API_KEY}"
        )

        geo_data = requests.get(geo_url).json()

        if not geo_data:
            return None

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        air_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )

        air_data = requests.get(air_url).json()

        if "list" not in air_data or not air_data["list"]:
            return None

        comp = air_data["list"][0]["components"]

        input_data = pd.DataFrame([{
            "PM2.5": comp["pm2_5"],
            "PM10": comp["pm10"],
            "NO2": comp["no2"],
            "CO": comp["co"],
            "SO2": comp["so2"],
            "O3": comp["o3"]
        }])

        prediction = round(model.predict(input_data)[0], 2)
        return prediction

    except Exception as e:
        print("Error for", city_name, ":", e)
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    global latest_data

    if request.method == "GET":
        latest_data = {
            "city": None,
            "prediction": None,
            "category": None,
            "pollutants": None,
            "forecast": None
        }

    city = latest_data["city"] if latest_data["city"] else ""
    prediction = latest_data["prediction"]
    category = latest_data["category"]
    pollutants = latest_data["pollutants"]
    forecast = latest_data["forecast"]

    if request.method == "POST":
        # Keep ALL your existing POST code here exactly as it is.

        city = request.form["city"]

        global recent_cities

        if city and city not in recent_cities:
            recent_cities.insert(0, city)

        if len(recent_cities) > 5:
            recent_cities.pop()

        try:

            # Get coordinates
            geo_url = (
                f"http://api.openweathermap.org/geo/1.0/direct"
                f"?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
            )

            geo_data = requests.get(geo_url).json()

            if not geo_data:
                return render_template(
                    "index.html",
                    city=city,
                    error="City not found. Please check the spelling and try again.",
                    prediction=None,
                    category=None,
                    pollutants=None,
                    forecast=None
                )

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]

            # Get air pollution data
            air_url = (
                f"http://api.openweathermap.org/data/2.5/air_pollution"
                f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
            )

            air_data = requests.get(air_url).json()
            if "list" not in air_data or not air_data["list"]:
                return render_template(
                    "index.html",
                    city=city,
                    error="No AQI prediction available for this location.",
                    prediction=None,
                    category=None,
                    pollutants=None,
                    forecast=None
                )

            comp = air_data["list"][0]["components"]

            input_data = pd.DataFrame([{
                "PM2.5": comp["pm2_5"],
                "PM10": comp["pm10"],
                "NO2": comp["no2"],
                "CO": comp["co"],
                "SO2": comp["so2"],
                "O3": comp["o3"]
            }])

            # Current AQI Prediction
            prediction = round(model.predict(input_data)[0], 2)

            # AQI Category
            category = get_aqi_category(prediction)

            # Pollutants
            pollutants = {
                "PM2.5": comp["pm2_5"],
                "PM10": comp["pm10"],
                "NO2": comp["no2"],
                "CO": comp["co"],
                "SO2": comp["so2"],
                "O3": comp["o3"]
            }

            # -------------------------
            # 7-Day AQI Forecast
            # -------------------------

            history = [prediction] * 7

            forecast = []

            for _ in range(7):

                forecast_input = pd.DataFrame(
                    [history[-7:]],
                    columns=[
                        "AQI_lag1",
                        "AQI_lag2",
                        "AQI_lag3",
                        "AQI_lag4",
                        "AQI_lag5",
                        "AQI_lag6",
                        "AQI_lag7"
                    ]
                )

                next_aqi = forecast_model.predict(forecast_input)[0]

                forecast.append(round(next_aqi))

                history.append(next_aqi)

            print("Current AQI:", prediction)
            print("Forecast:", forecast)


            latest_data = {
                "city": city,
                "prediction": prediction,
                "category": category,
                "pollutants": pollutants,
                "forecast": forecast
            }
            

        except Exception as e:
            print("========== FULL ERROR ==========")
            traceback.print_exc()
            print("===============================")

    return render_template(
        "index.html",
        city=city,
        prediction=prediction,
        category=category,
        pollutants=pollutants,
        forecast=forecast,
        recent_cities=recent_cities
       
    )


@app.route("/dashboard")
def dashboard():

    cities = [
        ("Delhi", "New Delhi,IN"),
        ("Ghaziabad", "Ghaziabad,IN"),
        ("Noida", "Noida,IN"),
        ("Gurugram", "Gurugram,IN"),
        ("Faridabad", "Faridabad,IN"),
        ("Kanpur", "Kanpur,IN"),
        ("Lucknow", "Lucknow,IN"),
        ("Patna", "Patna,IN"),
        ("Agra", "Agra,IN"),
        ("Varanasi", "Varanasi,IN"),
        ("Meerut", "Meerut,IN"),
        ("Muzaffarpur", "Muzaffarpur,IN"),
        ("Ludhiana", "Ludhiana,IN"),
        ("Amritsar", "Amritsar,IN"),
        ("Jaipur", "Jaipur,IN")
    ]

    city_aqi = {}

    for display_name, api_name in cities:
        aqi = get_city_aqi(api_name)
        print(display_name, "->", aqi)

        if aqi is not None:
            city_aqi[display_name] = aqi

    top5 = dict(
        sorted(city_aqi.items(), key=lambda item: item[1], reverse=True)[:5]
    )

    print("Top 5:", top5)

    if latest_data["prediction"] is None:
        return "Please search a city first from Home page."

    return render_template(
        "dashboard.html",
        city=latest_data["city"],
        prediction=latest_data["prediction"],
        category=latest_data["category"],
        pollutants=latest_data["pollutants"],
        forecast=latest_data["forecast"],
        top5=top5
    )



@app.route("/forecast")
def forecast_page():
    if latest_data["prediction"] is None:
        return "Please search a city first from Home page."

    return render_template(
        "forecast.html",
        city=latest_data["city"],
        prediction=latest_data["prediction"],
        category=latest_data["category"],
        pollutants=latest_data["pollutants"],
        forecast=latest_data["forecast"]
    )

@app.route("/clear")
def clear():
    global latest_data

    latest_data = {
        "city": None,
        "prediction": None,
        "category": None,
        "pollutants": None,
        "forecast": None
    }

    return redirect("/")

@app.route('/impact')
def impact():
    return render_template('impact.html')


if __name__ == "__main__":
    app.run(debug=True)