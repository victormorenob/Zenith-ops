"""Custom exceptions for the inference pipeline."""


class ModelNotFoundError(Exception):
    """Raised when the requested model_id is not found."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        super().__init__(f"No model found with id: {model_id}")


class InferenceTimeoutError(Exception):
    """Raised when inference exceeds the configured timeout."""

    def __init__(self, timeout_ms: int) -> None:
        super().__init__(f"Inference took longer than {timeout_ms}ms")


class InferenceError(Exception):
    """Raised when the model fails during inference."""

    def __init__(self, message: str = "Model failed during inference") -> None:
        super().__init__(message)
