class BaseModel:
    def __init__(self):
        self.best_model = None
        self.best_score = None

    def train(self, X, y):
        raise NotImplemented("Train method must be implemented by subclass.")
    
    def evaluate(self, X, y):
        if self.best_model is None:
            raise Exception("Model has not been trained yet!")
        return self.best_model.score(X, y)