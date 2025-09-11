# torch_test.py

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np
import exlog
import json

# Load dataset
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Convert to torch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)

# Define a simple sequential model (not defined in __main__)
model = nn.Sequential(
    nn.Linear(4, 10),
    nn.ReLU(),
    nn.Linear(10, 3),
    nn.Softmax(dim=1)
)

# Train the model
optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()
model.train()

for epoch in range(10):
    optimizer.zero_grad()
    output = model(X_train_tensor)
    loss = criterion(output, y_train_tensor)
    loss.backward()
    optimizer.step()

# Use exlog
print("Torch model class:", model.__class__)
print("Torch model module:", model.__class__.__module__)
framework = exlog.detect_framework(model)
print("Framework detected:", framework)

# Log explanations
logs = exlog.log(model, X_test, y_test, path="torch_log.json", sample_size=30)

# Print a sample
print("Torch test passed. Sample log:")
print(json.dumps(logs[0], indent=2))
