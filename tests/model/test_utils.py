from model.utils import reset_index_by_time, run_length_encode


def test_reset_index_by_time():
    src = [0, 3, 1, 1, 2, 2]
    tgt = [0, 1, 2, 2, 3, 3]
    assert reset_index_by_time(src) == tgt


def test_run_length_encode():
    src = "HHL"
    tgt = ["H2", "H2", "L1"]
    assert run_length_encode(src) == tgt

    src = "HL"
    tgt = ["H1", "L1"]
    assert run_length_encode(src) == tgt

    src = "HLL"
    tgt = ["H1", "L2", "L2"]
    assert run_length_encode(src) == tgt
