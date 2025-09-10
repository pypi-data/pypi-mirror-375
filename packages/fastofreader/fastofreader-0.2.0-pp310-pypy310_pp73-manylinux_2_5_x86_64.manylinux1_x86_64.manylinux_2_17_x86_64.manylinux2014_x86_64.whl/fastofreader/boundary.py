from __future__ import annotations

from typing import Dict


def read_boundary(path: str) -> Dict[str, Dict[str, int]]:
    """
    Parse an OpenFOAM boundary file and return a mapping:

    { boundaryName: {"nFaces": int, "startFace": int}, ... }

    The parser is lenient: ignores headers/comments and unrelated keys.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    result: Dict[str, Dict[str, int]] = {}
    name: str | None = None
    in_block = False
    nFaces: int | None = None
    startFace: int | None = None

    def commit():
        nonlocal name, nFaces, startFace
        if name is not None:
            result[name] = {
                "nFaces": int(nFaces or 0),
                "startFace": int(startFace or 0),
            }
        name = None
        nFaces = None
        startFace = None

    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("//"):
            continue
        if s.startswith("/*") or s.endswith("*/") or s.startswith("*"):
            continue
        if s in ("(", ")"):
            continue

        # Detect start of boundary block: a single token line (name) followed by '{'
        if not in_block and s not in ("{", "}") and all(ch not in s for ch in ";:() "):
            name = s
            continue

        if s == "{" and name is not None:
            in_block = True
            nFaces = None
            startFace = None
            continue

        if s == "}" and in_block:
            in_block = False
            commit()
            continue

        if in_block:
            if s.startswith("nFaces"):
                # e.g. nFaces          1000;
                parts = s.split()
                if len(parts) >= 2:
                    val = parts[1].rstrip(";")
                    try:
                        nFaces = int(val)
                    except ValueError:
                        pass
            elif s.startswith("startFace"):
                parts = s.split()
                if len(parts) >= 2:
                    val = parts[1].rstrip(";")
                    try:
                        startFace = int(val)
                    except ValueError:
                        pass

    return result
