import pandas as pd

# Load dataset
df = pd.read_csv("data/city_day.csv")

# Keep only needed columns
df = df[["City", "Date", "AQI"]]

# Convert date
df["Date"] = pd.to_datetime(df["Date"])

# Remove missing AQI
df = df.dropna(subset=["AQI"])

# Sort data
df = df.sort_values(["City", "Date"])

# Create lag features
for i in range(1, 8):
    df[f"AQI_lag{i}"] = df.groupby("City")["AQI"].shift(i)

# Target = next day's AQI
df["Target"] = df.groupby("City")["AQI"].shift(-1)

# Remove empty rows
df = df.dropna()

print(df.head())
print(df.shape)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

features = [
    "AQI_lag1",
    "AQI_lag2",
    "AQI_lag3",
    "AQI_lag4",
    "AQI_lag5",
    "AQI_lag6",
    "AQI_lag7"
]

X = df[features]
y = df["Target"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("R2 Score:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

joblib.dump(model, "models/forecast_model.pkl")

print("Forecast Model Saved Successfully!")