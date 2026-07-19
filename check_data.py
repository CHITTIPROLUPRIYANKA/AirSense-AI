import pandas as pd

df = pd.read_csv("data/city_day.csv")

print(df.head())

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)