import warnings

warnings.filterwarnings(
    "ignore", message = "X does not have valid feature names*" 
)
import shap
from ..saver import log_saver
from sklearn.base import is_classifier, is_regressor
def lightgbm_logger(model, X, y, path):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    if is_classifier(model):
        type_ = "classifier"
    if is_regressor(model):
        type_ = "regressor"
    return log_saver("lightgbm","TreeExplainer",model, shap_values, X, y, path, "tree" ,type_)
