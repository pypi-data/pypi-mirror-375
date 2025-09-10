from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from .base import BaseModel


class DecisionTreeModel(BaseModel):
    """
    Decision Tree for classification or regression
    Use "task" param to specify "classification" or "regression"
    Brute force search included
    """

    def __init__(self, task="classification", param_grid=None):
        super().__init__()
        self.task = task
        self.param_grid = param_grid or {
            "max_depth": [None, 3, 5, 10],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4]
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        if self.task.lower() == "classification":
            ModelClass = DecisionTreeClassifier
        else:
            ModelClass = DecisionTreeRegressor
        
        for max_depth in self.param_grid["max_depth"]:
            for min_samples_split in self.param_grid["min_samples_split"]:
                for min_samples_leaf in self.param_grid["min_samples_leaf"]:
                    model = ModelClass(
                        max_depth=max_depth,
                        min_samples_split=min_samples_split,
                        min_samples_leaf=min_samples_leaf
                    )
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model