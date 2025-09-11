import shap
import warnings
import numpy as np
from ..saver import log_saver

def torch_tensorflow_logger(model, X, y, path, sample_size):
    framework = detect_framework(model)
    if framework == "torch":
        try:
            import torch
        except ImportError:
            warnings.warn("'torch' is not installed. Run 'pip install mlexlog[torch]' to use this feature")
            return None
    if framework == "tensorflow":
        try:
            import tensorflow
        except ImportError:
            warnings.warn("'tensorflow' is not installed. Run 'pip install mlexlog[tensorflow]' to use this feature")
            return None
    if hasattr(X, "values"):
        X_np = X.values 
    else:
        X_np = X   
    X_sample = X_np[:sample_size]
    def predict_fn(x_numpy):
        with torch.no_grad():
            x_tensor = torch.tensor(x_numpy, dtype=torch.float32)
            output = model(x_tensor)
            return output.numpy()
    if framework == "torch":
        try:
            X_tensor_sample = torch.tensor(X_sample, dtype = torch.float32)
            explainer = shap.DeepExplainer(model, X_tensor_sample)
            shap_values = explainer(torch.tensor(X_np, dtype = torch.float32))
            return log_saver("torch", "DeepExplainer", model, shap_values, X, y, path, family = "neural network", task = "unknown")
        except Exception as e:
            warnings.warn(f"DeepExplainer failed for torch: {e}, using KernelExplainer on a sample dataset instead...")
    elif framework == "tensorflow":
        try:
            explainer = shap.DeepExplainer(model, X_sample)
            shap_values = explainer(X_np)
            return log_saver("tensorflow", "DeepExplainer", model,shap_values ,X, y, path, family = "neural network", task = "unknown")
        except Exception as e:
            warnings.warn(f"DeepExplainer failed for tensorflow: {e}, using KernelExplainer on a sample dataset instead...")

    if hasattr(model, "predict_proba"):
        f = model.predict_proba(X_sample)
    elif framework == "tensorflow":
        f = model.predict
    elif framework == "torch":
        f = predict_fn
    else:
        f = lambda x: model.predict(x)
            
    explainer = shap.KernelExplainer(f, X_sample)
    shap_values = explainer(X_sample)
    return log_saver(framework, "KernelExplainer", model, shap_values, X, y, path, family = "neural network",task = "unknown")

def detect_framework(model):
    cls = model.__class__.__module__
    if "torch" in cls:
        return "torch"
    elif "tensorflow" in cls or "keras" in cls:
        return "tensorflow"
    