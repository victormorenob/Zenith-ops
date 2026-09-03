"""Unit tests for model type registry / build_model (Phase C).

Tests cover:
  - build_model returns known model instances
  - build_model raises ValueError for unknown types
"""

from __future__ import annotations

import pytest

from zenith_ops.core.model_builders import _MODEL_BUILDERS, build_model


class TestModelBuilders:
    """Model type registry resolves type names to model instances."""

    def test_dummy_iris_is_registered(self) -> None:
        """'dummy_iris' must be in the builders dict."""
        assert "dummy_iris" in _MODEL_BUILDERS

    def test_build_dummy_iris_returns_instance(self) -> None:
        """build_model('dummy_iris') returns a DummyIrisClassifier."""
        model = build_model("dummy_iris")
        from zenith_ops.core.dummy_model import DummyIrisClassifier

        assert isinstance(model, DummyIrisClassifier)

    def test_dummy_iris_has_predict_method(self) -> None:
        """The built model instance has a working predict method."""
        model = build_model("dummy_iris")
        result = model.predict({"sepal_length": 5.1})
        assert result == 0.0

    def test_dummy_iris_predict_proba_returns_three_class_distribution(self) -> None:
        """Dummy Iris model returns the expected stable probability vector."""
        # Arrange
        from zenith_ops.core.dummy_model import DummyIrisClassifier

        model = DummyIrisClassifier()

        # Act
        probabilities = model.predict_proba({"sepal_length": 5.1})

        # Assert
        assert probabilities == [0.98, 0.01, 0.01]
        assert sum(probabilities) == pytest.approx(1.0)

    def test_unknown_type_raises_value_error(self) -> None:
        """An unrecognized model type raises ValueError."""
        with pytest.raises(ValueError, match="desconocido"):
            build_model("nonexistent_model")
