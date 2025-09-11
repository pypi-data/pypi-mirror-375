import shap
from ..saver import log_saver

def model_type(model):
        output = []
        name = model.__class__.__name__.lower()
        module = model.__class__.__module__.lower()
        if hasattr(model, "coef_"):
                output.append("linear")
                type_ = model._estimator_type
        elif hasattr(model, "tree_") or hasattr(model, "estimators_"):
                output.append("tree")
                type_ = model._estimator_type
        elif hasattr(model, "support_vectors_") or "svm" in module or "svc" in name or "svr" in name:
                output.append("svm")
                type_ = model._estimator_type
        elif "neighbors" in module or "kneighbors" in dir(model):
                output.append("neighbors")
                type_ = model._estimator_type
        elif "naive_bayes" in module:
                output.append("naive_bayes")
                type_ = model._estimator_type
        else:
                output.append("unknown")
                type_ = "unknown"
        output.append(type_)
        return output


def sklearn_logger(model, X, y, path, sample_size):
        explainer_name = None
        output = model_type(model)
        family = output[0]
        task = output[1]

        if family == "linear":
                explainer = shap.Explainer(model , X)
                shap_values = explainer(X)
                explainer_name = "Explainer"
        elif family == "tree":
                explainer = shap.Explainer(model , X)
                shap_values = explainer(X, check_additivity = False)
                explainer_name = "Explainer"
        elif family == "svm" or family == "neighbors" or family == "naive_bayes" or family == "unknown":
                print(f"Model not supported by explainer in shap... using kernelExplainer. using a sample for speed...")
                sample = X[:sample_size]
                if hasattr(model, "predict_proba"):
                        explainer = shap.KernelExplainer(lambda x: model.predict_proba(x) , sample)
                else:
                        explainer = shap.KernelExplainer(lambda x: model.predict(x) , sample)
                explainer_name = "KernelExplainer"
                shap_values = explainer(sample)
        else:
                raise ValueError(f"Unsupported model type: {family}")
        return log_saver("sklearn",explainer_name ,model, shap_values, X , y, path, family ,task)

