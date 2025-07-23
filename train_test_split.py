import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# ✅ Step 1: Load dataset (only ONE at a time)
data = pd.read_csv("jee_main_data.csv")

# ✅ Step 2: View actual column names to debug
print("Columns:", data.columns.tolist())

# ✅ Step 3: Rename columns to remove unwanted spaces (safe approach)
data.columns = data.columns.str.strip()

# ✅ Step 4: Features & Target
X = data[["Rank", "Seat Type", "Gender", "Quota"]]
y = data["Institute"]

# ✅ Step 5: Encode categorical output
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ✅ Step 6: Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# ✅ Step 7: Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# ✅ Step 8: Evaluate accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("✅ Model Accuracy:", round(accuracy * 100, 2), "%")
