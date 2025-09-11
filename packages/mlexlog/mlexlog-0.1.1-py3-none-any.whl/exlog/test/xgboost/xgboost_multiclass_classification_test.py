import exlog
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# Load multiclass dataset
X, y = load_iris(return_X_y=True)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost multiclass classifier
model = XGBClassifier(use_label_encoder=False, eval_metric="mlogloss")
model.fit(X_train, y_train)

# Run exlog
logs = exlog.log(model, X_test, y_test, path="xgboost_multiclass.json", sample_size=50)

# Print first record for inspection
import json
print(json.dumps(logs[0], indent=2))
