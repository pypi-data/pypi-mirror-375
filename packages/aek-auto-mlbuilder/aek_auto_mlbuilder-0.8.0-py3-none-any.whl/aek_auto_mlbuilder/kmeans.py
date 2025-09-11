from sklearn.cluster import KMeans
from .base import BaseModel


class KMeansModel(BaseModel):
    """
    K-Means clustering model (unsupervised learning)
    Brute force method has been using
    """
    def __init__(self, param_grid=None):
        super().__init__()
        self.param_grid = param_grid or {
            "n_clusters": [2, 3, 4, 5, 6],
            "init": ["k-means++", "random"],
            "n_init": [10, 20],
            "max_iter": [300, 500]
        }

    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        for n_clusters in self.param_grid["n_clusters"]:
            for init in self.param_grid["init"]:
                for n_init in self.param_grid["n_init"]:
                    for max_iter in self.param_grid["max_iter"]:
                        model = KMeans(
                            n_clusters=n_clusters,
                            init=init,
                            n_init=n_init,
                            max_iter=max_iter,
                            random_state=42
                        )
                        model.fit(X, y)
                        score = -model.inertia_
                        if score > best_score:
                            best_score = score
                            best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model
