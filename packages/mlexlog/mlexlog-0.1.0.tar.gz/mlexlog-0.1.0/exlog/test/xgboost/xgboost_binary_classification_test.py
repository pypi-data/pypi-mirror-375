# test_xgboost.py
import xgboost as xgb
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import exlog

# 1. Load dataset
X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Train an XGBoost classifier
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
model.fit(X_train, y_train)

# 3. Evaluate quickly
preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

# 4. Run through your exlog
logs = exlog.log(model, X_test, y_test, path="xgboost_logs.json")

# 5. Print sample of the log
print("First log entry:", logs[0])
