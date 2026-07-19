import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error



# Load dataset
df = pd.read_csv("data/city_day.csv")


# Features and target
features = [
    "PM2.5",
    "PM10",
    "NO2",
    "CO",
    "SO2",
    "O3"
]

target = "AQI"

# Keep required columns
df = df[features + [target]]

# Fill missing values
for col in features:
    df[col] = df[col].fillna(df[col].median())

# Remove rows with missing AQI
df = df.dropna(subset=[target])

# Split data
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Accuracy
print("R2 Score:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# Save model
joblib.dump(model, "models/aqi_model.pkl")

print("Model Saved Successfully!")