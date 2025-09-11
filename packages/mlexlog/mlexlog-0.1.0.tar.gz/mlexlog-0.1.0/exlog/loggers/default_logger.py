import shap
import warnings
from ..saver import log_saver
  
def default_logger(model, X, y, path, sample_size):
    warnings.warn(f"couldn't recognize the framework of the given model... couldn't output explainations")
    
    
