import xgboost as xgb
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import exlog

# Load regression dataset
X, y = fetch_california_housing(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train an XGBoost regressor
model = xgb.XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Evaluate (optional sanity check)
preds = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, preds))

# Run through exlog
logs = exlog.log(model, X_test, y=y_test, path="xgboost_regression.json", sample_size=50)

# Print a sample log
print(logs[0])
