<div align="center">
  <img src="https://raw.githubusercontent.com/alpemre8/aek-img-trainer/main/logo.png" alt="AEK Auto ML Builder Logo" width="400"/>
  
  # AEK Auto ML Builder
  
  Auto ML Builder Library 
</div>

# Installation


```bash
pip install aek-auto-mlbuilder
```
For future updates:
```bash
pip install --upgrade aek-auto-mlbuilder
```

# Usage


## Create LinearRegression model

For your linear regression problems, you can use LinearRegressor class via:(for now we use syntetic data):
```python
from aek_auto_mlbuilder import LinearRegressor
from sklearn.datasets import make_regression

X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)

lr = LinearRegressor()
lr.train(X, y)
print("Best Score:", lr.best_score)
```
