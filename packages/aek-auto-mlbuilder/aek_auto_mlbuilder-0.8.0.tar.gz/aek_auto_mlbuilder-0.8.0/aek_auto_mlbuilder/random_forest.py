from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from .base import BaseModel

class RandomForestModel(BaseModel):
    """
    Random Forest model for classification or regression
    Use task either "classification" or "regression"
    brute force method has been using
    """
    def __init__(self, task="classification", param_grid=None):
        super().__init__()
        self.task = task
        self.param_grid = param_grid or {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 5, 10],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2]
        }
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        if self.task.lower() == "classification":
            ModelClass = RandomForestClassifier
        elif self.task.lower() == "regression":
            ModelClass = RandomForestRegressor
        else:
            raise ValueError("task must be 'classification' or 'regression'")
        
        for n_estimators in self.param_grid["n_estimators"]:
            for max_depth in self.param_grid["max_depth"]:
                for min_samples_split in self.param_grid["min_samples_split"]:
                    for min_samples_leaf in self.param_grid["min_samples_leaf"]:
                        model = ModelClass(
                            n_estimators=n_estimators,
                            max_depth=max_depth,
                            min_samples_split=min_samples_split,
                            min_samples_leaf=min_samples_leaf,
                            random_state=42,
                            n_jobs=-1
                        )
                        model.fit(X, y)
                        score = model.score(X, y)
                        if score > best_score:
                            best_score = score
                            best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model
    