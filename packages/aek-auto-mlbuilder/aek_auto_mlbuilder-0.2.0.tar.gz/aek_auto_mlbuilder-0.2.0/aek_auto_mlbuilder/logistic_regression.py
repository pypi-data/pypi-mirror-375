from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from .base import BaseModel



class LogisticClassifier(BaseModel):
    """
    Basic Logistic Regression class for binary/multi-class classification.
    Brute-force parameter search included.
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "C": [0.01, 0.1, 1, 10],
            "penalty": ["l2"],
            "solver": ["lbfgs"],
            "fit_intercept": [True, False]
        }
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for C in self.param_grid["C"]:
            for penalty in self.param_grid["penalty"]:
                for solver in self.param_grid["solver"]:
                    for fit_intercept in self.param_grid["fit_intercept"]:
                        model = make_pipeline(
                            StandardScaler(),
                            LogisticRegression(
                                C=C,
                                penalty=penalty,
                                solver=solver,
                                fit_intercept=fit_intercept,
                                max_iter=1000
                            )
                        )
                        model.fit(X, y)
                        score = model.score(X, y)
                        if score > best_score:
                            best_score = score
                            best_model = model
        
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model