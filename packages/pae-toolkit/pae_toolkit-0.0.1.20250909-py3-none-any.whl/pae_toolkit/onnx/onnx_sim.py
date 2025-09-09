import logging
from pathlib import Path

import onnx
from onnxsim import simplify


def simplify_onnx(filename: str | Path):
    if not isinstance(filename, Path):
        filename = Path(filename)

    model = onnx.load(filename)
    model_simp, check = simplify(model)

    assert check, "Simplified ONNX model could not be validated"
    new_filename = filename.with_name(f"{filename.stem}_sim.onnx")
    onnx.save_model(model_simp, new_filename)
    logging.info(f"Saved simplified ONNX model to {new_filename}")
