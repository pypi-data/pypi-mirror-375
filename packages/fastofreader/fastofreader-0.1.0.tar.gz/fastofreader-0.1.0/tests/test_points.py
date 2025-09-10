from fastofreader import read_points

def test_read_points_triplets():
    pts = read_points("points_test_file")
    assert len(pts) == 4
    assert pts[0] == [0.0, 0.0, 0.0]
    assert pts[1][0] == 1e-05
    assert abs(pts[-1][0] - 0.009565012) < 1e-12
    assert abs(pts[-1][1] - 2.53949e-07) < 1e-15
    assert abs(pts[-1][2] - 0.0003300763) < 1e-15