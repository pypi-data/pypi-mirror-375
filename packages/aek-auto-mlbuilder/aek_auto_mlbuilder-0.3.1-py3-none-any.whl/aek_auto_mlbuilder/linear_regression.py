from sklearn.linear_model import LinearRegression
from .base import BaseModel
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class LinearRegressor(BaseModel):
    """
    Basic Linear Regression class
    Try parameters with brute-force.
    """

    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "fit_intercept": [True, False],
            "normalize": [True, False]
        }
    
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for fit_intercept in self.param_grid["fit_intercept"]:
            for normalize in self.param_grid["normalize"]:
                
                if normalize:
                    model = make_pipeline(StandardScaler(), LinearRegression(fit_intercept=fit_intercept))
                else:
                    model = LinearRegression(fit_intercept=fit_intercept)

                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model

        self.best_model = best_model
        self.best_score = best_score
        return self.best_model