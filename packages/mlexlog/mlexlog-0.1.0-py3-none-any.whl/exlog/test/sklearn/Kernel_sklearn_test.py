import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import exlog
X, y = datasets.load_breast_cancer(return_X_y=True)
X = X[:200]
y = y[:200]
model = SVC(probability=True, kernel="rbf", random_state=42)
model.fit(X, y)
print(">>> Running exlog on SVM...")
logs = exlog.log(model, X, y, path="svm_logs.json", sample_size=50)
print("Number of logs:", len(logs))
print("First log sample:\n", logs[0])
