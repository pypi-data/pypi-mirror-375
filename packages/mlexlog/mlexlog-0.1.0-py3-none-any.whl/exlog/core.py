### Our core intention in this entire process is to figure out the type of model that we are dealing with, and then give the most optimal explaination for the given model.
from pathlib import Path
from .loggers import sklearn_logger, xgboost_logger, lightgbm_logger, torch_tensorflow_logger, default_logger

### We will first try to figure out the framework type with the help of python's __class__ and __module__ dunder attributes.
def detect_framework(model):
    cls = model.__class__.__module__.lower()
    print(cls)
    if "xgboost" in cls:
        return "xgboost"
    if "lightgbm" in cls:
        return "lightgbm"
    if "sklearn" in cls:
        return "sklearn"
    if "torch" in cls:
        return "torch"
    if "tensorflow" in cls or "keras" in cls:
        return "tensorflow"
    return "unknown"

### We are going to assign a seperate function for the user's request depending upon the framework we are dealing with. Each function here solves the explanation problem in their unqiue way.
def log(model, X, y = None, path = "exlog.json", sample_size = 100):
    framework = detect_framework(model)
    if framework == "sklearn":
        return sklearn_logger(model, X, y, path, sample_size)
    elif framework == "xgboost":
        return xgboost_logger(model, X, y, path)
    elif framework == "lightgbm":
        return lightgbm_logger(model, X, y, path)
    elif framework == "torch" or framework == "tensorflow":
        return torch_tensorflow_logger(model, X, y, path, sample_size)
    else:
        print(f"The framework '{framework}' is not supported. Falling back to kernel explainer...")
        return default_logger(model, X , y, path, sample_size)      