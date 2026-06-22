"""Tests for custom exception classes."""

from zenith_ops.core.exceptions import (
    DuplicateModelError,
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


class TestDuplicateModelError:
    """TDD Cycle: A.6 — DuplicateModelError exception."""

    def test_inherits_from_zenitherror(self) -> None:
        """DuplicateModelError MUST be a subclass of Zenitherror."""
        from zenith_ops.core.exceptions import Zenitherror

        assert issubclass(DuplicateModelError, Zenitherror)

    def test_message_format(self) -> None:
        """Exception message MUST include name and version."""
        err = DuplicateModelError(name="iris", version="1.0.0")
        assert "iris" in str(err)
        assert "1.0.0" in str(err)

    def test_name_attribute(self) -> None:
        """Exception MUST expose the name attribute."""
        err = DuplicateModelError(name="test-model", version="2.0.0")
        assert err.name == "test-model"

    def test_version_attribute(self) -> None:
        """Exception MUST expose the version attribute."""
        err = DuplicateModelError(name="test-model", version="2.0.0")
        assert err.version == "2.0.0"
