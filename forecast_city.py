import pandas as pd

city = "Ahmedabad"

df = pd.read_csv("data/city_day.csv")

df = df[["City", "Date", "AQI"]]
df = df.dropna()

city_df = df[df["City"] == city]

city_df = city_df.sort_values("Date")

print(city_df.tail(10))