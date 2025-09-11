from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from .base import BaseModel


class KNNModel(BaseModel):
    """
    KNN model for classification for classification or regression
    Use "task" for "classification" or "regression"
    Brute-force search has been using
    """
    def __init__(self, task="classification", param_grid=None):
        super().__init__()
        self.task = task
        self.param_grid = param_grid or {
            "n_neighbors": [3, 5, 7, 9],
            "weights": ["uniform", "distance"],
            "p": [1, 2] #1: manhattan, 2: euclidean
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        if self.task.lower() == "classification":
            ModelClass = KNeighborsClassifier
        elif self.task.lower() == "regression":
            ModelClass = KNeighborsRegressor
        else:
            raise ValueError("task must be 'classification' or 'regression'")
        
        for n in self.param_grid["n_neighbors"]:
            for weights in self.param_grid["weights"]:
                for p in self.param_grid["p"]:
                    model = make_pipeline(
                        StandardScaler(),
                        ModelClass(n_neighbors=n, weights=weights, p=p)
                    )
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model

        self.best_model = best_model
        self.best_score = best_score
        return self.best_model