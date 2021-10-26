from model.modeler import Modeler


def test_test():
    src = ["H2", "H2", "H2", "dL1", "dL1"]
    tgt = "HHL"
    assert tgt == Modeler.to_pattern(src)
