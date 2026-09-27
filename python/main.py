"""Arduino App Lab entry point for the R.O.B. Vision controller."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def controller_token() -> str:
    token = os.environ.get("ROB_VISION_TOKEN", "")
    if token:
        return token
    token_file = ROOT / "data" / "controller-token"
    try:
        return token_file.read_text().strip()
    except FileNotFoundError:
        raise RuntimeError(f"Controller token missing from {token_file}") from None


def main() -> None:
    from controller.service import serve
    from controller.matrix import MatrixDisplay, MatrixMode

    matrix = MatrixDisplay()
    matrix.send(MatrixMode.LOADING, force=True)
    token = controller_token()
    if not token:
        raise RuntimeError("Controller token is empty")
    serve("0.0.0.0", 8766, token, matrix=matrix)


if __name__ == "__main__":
    main()
