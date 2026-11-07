from pathlib import Path
import hashlib

MODEL_SHA256 = "ad7ac52397fee149f492ca865a7ed87c2962eaebffb25ccbce8688e6487f6ab6"

def verify_model_integrity(model_path: Path) -> None:
    hasher = hashlib.sha256()

    with model_path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            hasher.update(chunk)

    actual_hash = hasher.hexdigest()

    if actual_hash != MODEL_SHA256:
        raise RuntimeError("Model integrity verification failed")
