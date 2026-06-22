"""Generate a dummy .joblib model for local development and testing."""

import os

import joblib

from zenith_ops.core.dummy_model import DummyIrisClassifier


def main() -> None:
    """Pickle a DummyIrisClassifier to models/iris-classifier/1.0.0/model.joblib."""
    model = DummyIrisClassifier()
    os.makedirs("models/iris-classifier/1.0.0", exist_ok=True)
    joblib.dump(model, "models/iris-classifier/1.0.0/model.joblib")
    print("✅ Dummy model generated at models/iris-classifier/1.0.0/model.joblib")


if __name__ == "__main__":
    main()
