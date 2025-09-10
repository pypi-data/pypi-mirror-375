from fastofreader import read_boundary


def test_read_boundary_file():
    b = read_boundary("boundary_test_file")
    assert "inlet" in b and "outlet" in b
    assert b["inlet"]["nFaces"] == 1000
    assert b["inlet"]["startFace"] == 25419692
    assert b["upperWall"]["nFaces"] == 120000
    assert b["cellSurface"]["startFace"] == 26130822