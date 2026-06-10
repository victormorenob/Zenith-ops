"""Generate a dummy .joblib model for local development and testing."""

import joblib

from zenith_ops.core.dummy_model import DummyIrisClassifier


def main() -> None:
    """Pickle a DummyIrisClassifier to models/iris-classifier.joblib."""
    model = DummyIrisClassifier()
    joblib.dump(model, "models/iris-classifier.joblib")
    print("✅ Dummy model generated at models/iris-classifier.joblib")


if __name__ == "__main__":
    main()
