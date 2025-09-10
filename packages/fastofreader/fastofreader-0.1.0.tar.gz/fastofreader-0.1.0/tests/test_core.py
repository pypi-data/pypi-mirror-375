from fastofreader import read_faces

def test_read_faces_returns_16_groups():
    groups = read_faces("faces_test_file")
    assert len(groups) == 16
