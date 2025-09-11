import lightgbm as lgb
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from exlog import log  # adjust to your actual import

X, y = fetch_california_housing(return_X_y=True, as_frame=True)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define and train LightGBM regressor
model = lgb.LGBMRegressor()
model.fit(X_train, y_train)

# Run exlog logger (logs first 50 samples to keep output manageable)
logs = log(model, X_test, y_test, path="lightgbm_regression.json", sample_size=50)

# Optional: sanity check model performance
preds = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, preds))
print(logs[0])
