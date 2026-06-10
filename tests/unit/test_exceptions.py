"""Tests for custom exception classes."""

from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)


class TestModelNotFoundError:
    def test_message_format(self) -> None:
        err = ModelNotFoundError(model_id="iris-classifier")
        assert str(err) == "No model found with id: iris-classifier"

    def test_model_id_attribute(self) -> None:
        err = ModelNotFoundError(model_id="test-model")
        assert err.model_id == "test-model"


class TestInferenceTimeoutError:
    def test_message_format(self) -> None:
        err = InferenceTimeoutError(timeout_ms=5000)
        assert str(err) == "Inference took longer than 5000ms"

    def test_custom_timeout(self) -> None:
        err = InferenceTimeoutError(timeout_ms=1000)
        assert str(err) == "Inference took longer than 1000ms"


class TestInferenceError:
    def test_default_message(self) -> None:
        err = InferenceError()
        assert str(err) == "Model failed during inference"

    def test_custom_message(self) -> None:
        err = InferenceError(message="Custom error")
        assert str(err) == "Custom error"
