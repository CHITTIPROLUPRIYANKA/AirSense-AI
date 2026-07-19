import joblib

model = joblib.load("models/aqi_model.pkl")

sample = [[80, 120, 35, 2.5, 15, 50]]

prediction = model.predict(sample)

print("Predicted AQI:", prediction[0])