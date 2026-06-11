"""Dummy ML model for integration testing."""


class DummyIrisClassifier:
    """A mock classifier that always predicts class 0 (Iris-setosa)."""

    def predict(self, features: dict[str, float]) -> float:
        """Return a constant prediction regardless of input."""
        return 0.0

    def predict_proba(self, features: dict[str, float]) -> list[float]:
        """Return mock probability distribution over 3 Iris classes.

        [0.98, 0.01, 0.01] = 98% setosa, 1% versicolor, 1% virginica
        """
        return [0.98, 0.01, 0.01]
