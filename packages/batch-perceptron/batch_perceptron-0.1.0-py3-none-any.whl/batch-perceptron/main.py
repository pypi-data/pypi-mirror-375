import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

class Perceptron(BaseEstimator, ClassifierMixin):
  def __init__(self, learning_rate=0.01, epoch=100):
    self.weight = None
    self.bias = None
    self.learning_rate = learning_rate
    self.epoch = epoch

  def fit(self, X, y):
    n_samples, n_features = X.shape
    self.weight = np.zeros(n_features)
    self.bias = 0
    self.gradient_descent(X,y)
    return self # Added return self for compatibility

  def step(self, X):
    return np.where(X>0,1,-1)

  def hypothesis(self, X):
    return self.step(np.dot(X, self.weight) + self.bias)


  def gradient_descent(self,X,y):
    for i in range(1,self.epoch):
      # Calculate predictions for the entire batch
      predictions = self.hypothesis(X)

      # Identify misclassified samples (where y * f(x) <= 0)
      misclassified_indics= np.where(y*predictions<=0)[0]

      if len(misclassified_indics) == 0:
        print(f"Model converged at {self.epoch}")
        break

      # Calculate the total gradient for weights from misclassified samples
      # Gradient contribution for misclassified sample i and feature j is -yi * xij
      # Summing over misclassified samples: -sum(yi * xij) for each feature j
      # This is equivalent to np.dot(X[misclassified_indices].T, -self.y[misclassified_indices])

      gradient_w = np.dot(X[misclassified_indics].T,y[misclassified_indics])

      # Calculate the total gradient for bias from misclassified samples
      # Gradient contribution for misclassified sample i is -yi
      # Summing over misclassified samples: -sum(yi)

      gradient_b = np.sum(y[misclassified_indics])

      # Update weights and bias using the learning rate
      self.weight += self.learning_rate * gradient_w
      self.bias += self.learning_rate * gradient_b

    print(f"Finished training after {self.epoch} epochs")


  def predict(self, X):
      return self.hypothesis(X)

  def score(self, X, y):
      """Calculates the accuracy of the model."""
      predictions = self.predict(X)
      return np.mean(predictions == y)

  # Add get_params and set_params for GridSearchCV compatibility
  def get_params(self, deep=True):
      return {'learning_rate': self.learning_rate, 'epoch': self.epoch}

  def set_params(self, **parameters):
      for parameter, value in parameters.items():
          setattr(self, parameter, value)
      return self
