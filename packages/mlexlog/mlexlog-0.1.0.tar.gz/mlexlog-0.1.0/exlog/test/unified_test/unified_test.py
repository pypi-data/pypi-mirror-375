import numpy as np
from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
import xgboost as xgb
import lightgbm as lgb
import torch
import torch.nn as nn
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import exlog 

def run_tests():
    print("=== Running ML Logger Tests ===")
    iris_X, iris_y = load_iris(return_X_y=True)
    cal_X, cal_y = fetch_california_housing(return_X_y=True)
    X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(iris_X, iris_y, test_size=0.2, random_state=42)
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(cal_X, cal_y, test_size=0.2, random_state=42)
    models = [
        LogisticRegression(max_iter=200),
        LinearRegression(),
        RandomForestClassifier(),
        RandomForestRegressor(),
        SVC(probability=True),
        SVR(),
        KNeighborsClassifier(),
        KNeighborsRegressor(),
        GaussianNB()
    ]
    for model in models:
        print(f"\n--- Testing {model.__class__.__name__} ---")
        if hasattr(model, "_estimator_type") and model._estimator_type == "classifier":
            model.fit(X_train_i, y_train_i)
            logs = exlog.log(model, X_test_i, y_test_i, path=f"{model.__class__.__name__}_logs.json")
        else:
            model.fit(X_train_c, y_train_c)
            logs = exlog.log(model, X_test_c, y_test_c, path=f"{model.__class__.__name__}_logs.json")
        print("Sample log:", logs[0])

    xgb_clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb_clf.fit(X_train_i, y_train_i)
    logs = exlog.log(xgb_clf, X_test_i, y_test_i, path="XGBClassifier_logs.json")
    print("\n--- XGBoost Classifier Sample ---")
    print(logs[0])

    xgb_reg = xgb.XGBRegressor()
    xgb_reg.fit(X_train_c, y_train_c)
    logs = exlog.log(xgb_reg, X_test_c, y_test_c, path="XGBRegressor_logs.json")
    print("\n--- XGBoost Regressor Sample ---")
    print(logs[0])

    lgb_clf = lgb.LGBMClassifier()
    lgb_clf.fit(X_train_i, y_train_i)
    logs = exlog.log(lgb_clf, X_test_i, y_test_i, path="LGBClassifier_logs.json")
    print("\n--- LightGBM Classifier Sample ---")
    print(logs[0])

    lgb_reg = lgb.LGBMRegressor()
    lgb_reg.fit(X_train_c, y_train_c)
    logs = exlog.log(lgb_reg, X_test_c, y_test_c, path="LGBRegressor_logs.json")
    print("\n--- LightGBM Regressor Sample ---")
    print(logs[0])

    torch_model = nn.Sequential(
        nn.Linear(4, 10),
        nn.ReLU(),
        nn.Linear(10, 3)
    )
    torch_model.eval()
    logs = exlog.log(torch_model, X_test_i, None, path="TorchNN_logs.json")
    print("\n--- Torch NN Sample ---")
    print(logs[0])

    tf_model = Sequential([
        Dense(10, activation='relu', input_shape=(4,)),
        Dense(3, activation='softmax')
    ])
    tf_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    tf_model.fit(X_train_i, y_train_i, epochs=1, verbose=0)
    logs = exlog.log(tf_model, X_test_i, None, path="TFNN_logs.json")
    print("\n--- TensorFlow NN Sample ---")
    print(logs[0])

    class MyCustomModel:
        def predict(self, X):
            return np.zeros(len(X))
    custom_model = MyCustomModel()
    logs = exlog.log(custom_model, X_test_i, None, path="CustomModel_logs.json")
    print("\n--- Custom Model Sample ---")
    print(logs[0])
    
    print("\n=== All tests executed! ===")

run_tests()
