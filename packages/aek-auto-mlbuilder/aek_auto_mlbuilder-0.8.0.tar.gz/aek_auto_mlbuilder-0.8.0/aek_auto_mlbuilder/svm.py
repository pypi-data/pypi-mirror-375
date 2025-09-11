from sklearn.svm import SVC, SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from .base import BaseModel


class SVMModel(BaseModel):
    """
    support vector machine for classification and regression
    use task parameter for "regression" or "classification"
    brute force has been using
    """
    def __init__(self, task="classification", param_grid=None):
        super().__init__()
        self.task = task
        self.param_grid = param_grid or {
            "C": [0.1, 1, 10],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale", "auto"]
        }
    
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        if self.task.lower() == "classification":
            ModelClass = SVC
        elif self.task.lower() == "regression":
            ModelClass = SVR
        else:
            raise ValueError("task must be either classification or regression")
        
        for C in self.param_grid["C"]:
            for kernel in self.param_grid["kernel"]:
                for gamma in self.param_grid["gamma"]:
                    model = make_pipeline(
                        StandardScaler(),
                        ModelClass(C=C, kernel=kernel, gamma=gamma)
                    )
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model