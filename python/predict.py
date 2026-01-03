import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Load data
conn = sqlite3.connect("../sql/manufacturing.db")
df = pd.read_sql("SELECT * FROM validated_data", conn)
conn.close()

# Prepare data
df['process_step_encoded'] = df['process_step'].astype('category').cat.codes
features = ['measured_value', 'lower_limit', 'upper_limit', 'process_step_encoded']
X = df[features]
y = df['out_of_spec'].astype(int)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred)}")

# Save model
joblib.dump(model, "../sql/failure_predictor.pkl")
print("Model saved.")