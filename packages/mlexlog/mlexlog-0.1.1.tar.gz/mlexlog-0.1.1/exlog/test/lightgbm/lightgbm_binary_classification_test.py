import lightgbm as lgb
import shap
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import exlog

# Load dataset (binary classification)
X, y = load_breast_cancer(return_X_y=True, as_frame=False)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a LightGBM classifier
model = lgb.LGBMClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# Get predictions and accuracy
preds = model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, preds))

# Run your exlog logger
logs = exlog.log(model, X_test, y_test, path="lgbm_binary.json", sample_size=50)

# Show a sample log
print("Sample Log Entry:")
print(logs[0])
