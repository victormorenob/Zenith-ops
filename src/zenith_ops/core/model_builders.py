"""Model type registry — maps type names to model constructors.

Usage
-----
>>> from zenith_ops.core.model_builders import build_model
>>> model = build_model("dummy_iris")
>>> model.predict({"sepal_length": 5.1})
0.0
"""

from __future__ import annotations

from zenith_ops.core.dummy_model import DummyIrisClassifier

#: Registry of known model type names → constructors (classes).
_MODEL_BUILDERS: dict[str, type] = {
    "dummy_iris": DummyIrisClassifier,
}


def build_model(model_type: str) -> object:
    """Instantiate a model by type name.

    Parameters
    ----------
    model_type:
        A key in ``_MODEL_BUILDERS`` (e.g. ``"dummy_iris"``).

    Returns
    -------
    An instance of the registered model class.

    Raises
    ------
    ValueError
        If *model_type* is not a known key.
    """
    builder = _MODEL_BUILDERS.get(model_type)
    if builder is None:
        msg = f"Tipo de modelo desconocido: {model_type}"
        raise ValueError(msg)
    return builder()
