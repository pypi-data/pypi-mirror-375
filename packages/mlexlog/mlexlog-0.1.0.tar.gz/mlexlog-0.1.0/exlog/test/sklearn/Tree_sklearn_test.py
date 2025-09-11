from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import exlog

# Data + model
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

#cls = model.__class__.__module__
#print(cls)
# Run exlog
logs = exlog.log(model, X_test, y_test, path="iris_logs.json")

# Quick check
print("Number of logs:", len(logs))
print("First record sample:")
print(logs[0])
