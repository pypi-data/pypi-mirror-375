from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from .base import BaseModel


class NaiveBayesModel(BaseModel):
    """
    Naive bayes model supporting gaussianNB, multinomialNB, bernoulliNB
    use 'nb_type' param to specify the variant: gaussian, multinomial, bernoulli
    brute force hyperparameter search has been using
    """
    def __init__(self, nb_type="gaussian", param_grid=None):
        super().__init__()
        self.nb_type = nb_type.lower()

        if self.nb_type == "gaussian":
            
            self.param_grid = param_grid or {
                "var_smoothing": [1e-9, 1e-8, 1e-7]
            }
        elif self.nb_type == "multinomial":
            
            self.param_grid = param_grid or {
                "alpha": [1.0, 0.5, 0.1]
            }
        elif self.nb_type == "bernoulli":
            
            self.param_grid = param_grid or {
                "alpha": [1.0, 0.5, 0.1],
                "binarize": [0.0, 0.5, 1.0]
            }
        else:
            raise ValueError("nb_type must be 'gaussian', 'multinomial', 'bernoulli'")
        
    def train(self, X, y):
        best_score = -float("inf")
        best_model = None

        if self.nb_type == "gaussian":
            for var_smoothing in self.param_grid["var_smoothing"]:
                model = GaussianNB(var_smoothing=var_smoothing)
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
        elif self.nb_type == "multinomial":
            for alpha in self.param_grid["alpha"]:
                model = MultinomialNB(alpha=alpha)
                model.fit(X, y)
                score = model.score(X, y)
                if score > best_score:
                    best_score = score
                    best_model = model
        elif self.nb_type == "bernoulli":
            for alpha in self.param_grid["alpha"]:
                for binarize in self.param_grid["binarize"]:
                    model = BernoulliNB(alpha=alpha, binarize=binarize)
                    model.fit(X, y)
                    score = model.score(X, y)
                    if score > best_score:
                        best_score = score
                        best_model = model
        self.best_model = best_model
        self.best_score = best_score
        return self.best_model
