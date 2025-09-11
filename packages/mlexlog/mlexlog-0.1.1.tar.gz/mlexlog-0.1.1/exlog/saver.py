import json
import numpy as np
from pathlib import Path
import torch
def log_saver(framework, explainer, model, shap_values, X , y, path, family = None, task = None):
        
        logs = []
        for i in range(len(shap_values.values)):
            if isinstance(X, np.ndarray):
                row = X[i]
                if framework == "torch":
                    prediction = model(torch.tensor(row.reshape(1, - 1), dtype = torch.float32))[0]
                else:
                    prediction = model.predict(row.reshape(1, -1))[0]
            else:
                row = X.iloc[i]
                if framework == "torch":
                    prediction = model(torch.tensor([row.values], dtype = torch.float32))[0]
                else:
                    prediction = model.predict([row.values])[0]
            if isinstance(prediction, np.generic):
                prediction = prediction.item()
            if isinstance(prediction, np.ndarray):
                prediction = prediction.tolist()
            if isinstance(prediction, torch.Tensor) and prediction.dim() == 0:
                prediction = prediction.item()
            if isinstance(prediction, torch.Tensor):
                prediction = prediction.tolist()
            record = {
                "framework": framework,
                "family" : family,
                "task" : task,
                "Explainer": explainer,
                "Input": row.to_dict() if hasattr(row, "to_dict") else row.tolist(),
                "Prediction": prediction,
                "Explanation": shap_values.values[i].tolist()
            }

            if framework == "unknown":
                record["Message"] = "Framework not recognized"

            if y is not None:
                if task in ("classification", "classifier"):
                    record["Prediction State"] = bool(prediction == y[i])
                else:
                    record["Prediction State"] = None 

            logs.append(record)
        return json_file_saver(logs, path)

    ### We are converting the logs array into a json file and saving it in the given path. We are also returning the logs for further analysis by the user.
def json_file_saver(logs, path):
    Path(path).write_text(json.dumps(logs ,indent = 2))
    print(f"Logs have been saved to {path}.")
    return logs