import joblib
import pandas as pd

model = joblib.load("models/forecast_model.pkl")

history = [50, 55, 60, 58, 62, 65, 70]

forecast = []

for day in range(7):

    print("Running day:", day + 1)

    input_df = pd.DataFrame(
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

    pred = model.predict(input_df)[0]

    forecast.append(round(pred))
    history.append(pred)

print("Forecast length:", len(forecast))
print("7-Day Forecast:")
print(forecast)