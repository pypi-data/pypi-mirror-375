from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import json
import exlog
import tensorflow as tf
print("\n--- Running TensorFlow Test ---")
    
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(4,)),
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=5, verbose=0)

log_path = "tf_log.json"
logs = exlog.log(model, X_test, y_test, path=log_path, sample_size=50)

print("TF Test Passed. Sample log:")
print(json.dumps(logs[0], indent=2))
