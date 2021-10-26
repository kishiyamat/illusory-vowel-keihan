from model.modeler import Modeler
import pytest


def test_to_pattern():
    src = ["H2", "H2", "H2", "dL1", "dL1"]
    tgt = "HHL"
    assert tgt == Modeler.to_pattern(src)
    src = ["H1", "H1", "H1", "dL1", "dL1"]
    tgt = "HL"
    assert tgt == Modeler.to_pattern(src)


def test_X_by_K():
    Modeler._X_by_K
    pass


def test_duration_by_K():
    Modeler._duration_by_K
    pass


def test_startprob_tmat():
    Modeler._startprob_tmat
    pass


def test_duration_dist():
    dur_list = [8, 8, 10, 10, 20]  # 17--20 のintegralは0.2になる
    tgt = [0.00, 0.00, 0.00, 0.00,
           0.10, 0.10, 0.10, 0.10,
           0.10, 0.10, 0.10, 0.10,
           0.00, 0.00, 0.00, 0.00,
           0.05, 0.05, 0.05, 0.05, ]
    res = Modeler._duration_dist(dur_list, frame_max_len=20, conv=4).tolist()
    assert res == tgt
    with pytest.raises(ValueError):
        dur_list = [8, 8, 10, 10, 100]
        Modeler._duration_dist(dur_list, frame_max_len=20, conv=4)
