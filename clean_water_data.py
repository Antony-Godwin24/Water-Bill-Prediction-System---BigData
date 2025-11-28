import pandas as pd

# Load dataset
df = pd.read_csv("dataset/water_bill_data.csv")

# 1️⃣ Drop duplicates
df = df.drop_duplicates()

# 2️⃣ Drop empty or all-NaN columns
df = df.dropna(axis=1, how="all")

# 3️⃣ Convert Date_Time column to datetime
df["Date_Time"] = pd.to_datetime(df["Date_Time"], errors="coerce")

# 4️⃣ Remove rows where Date_Time couldn’t be parsed
df = df.dropna(subset=["Date_Time"])

# 5️⃣ Convert numeric fields safely
numeric_cols = df.select_dtypes(include=["object"]).columns
for col in numeric_cols:
    try:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    except:
        pass

# 6️⃣ Drop rows with missing target values (or replace with mean)
# Note: The dataset might still have 'Charging_Load_kW' if not manually updated.
# We check for both potential names.
target_col = "Water_Bill_Amount"
if "Charging_Load_kW" in df.columns:
    target_col = "Charging_Load_kW"

if target_col in df.columns:
    df[target_col] = df[target_col].fillna(df[target_col].mean())

# Save cleaned dataset
df.to_csv("dataset/water_bill_data_clean.csv", index=False)

print(f"✅ Cleaned dataset saved! Rows: {len(df)}, Columns: {len(df.columns)}")
