from model.path_manager import PathManager
from pathlib import Path


def test_trian_test_wav():
    train_wav_list, test_wav_list = PathManager.train_test_wav(is_test=True)
    test_wav_list.sort() 
    assert train_wav_list == ['esuko-LHH-1.wav']
    assert test_wav_list == ['esko-L_H-2.wav', 'esko-L_H-3.wav']


def test_data_path():
    # TODO: src_2 を wav に限定しない
    src_1, src_2 = "original", 'esuko-LHH-1.wav'
    tgt = Path("../src/audio/output/esuko-LHH-1.wav")
    assert PathManager.data_path(src_1, src_2) == tgt
    src_1, src_2 = "downsample", 'esuko-LHH-1.wav'
    tgt = Path("../model/wav/esuko-LHH-1.wav")
    assert PathManager.data_path(src_1, src_2) == tgt
    # numpy
    src_1, src_2 = "feature", 'esuko-LHH-1.wav'
    tgt = Path("../model/feature/esuko-LHH-1.npy")
    assert PathManager.data_path(src_1, src_2) == tgt
    src_1, src_2 = "pitch_delta", 'esuko-LHH-1.wav'
    tgt = Path("../model/pitch_delta/esuko-LHH-1.npy")
    assert PathManager.data_path(src_1, src_2) == tgt
    src_1, src_2 = "label_base", 'esuko-LHH-1.wav'
    tgt = Path("../model/label_base/esuko-LHH-1.npy")
    assert PathManager.data_path(src_1, src_2) == tgt
    src_1, src_2 = "label_rle", 'esuko-LHH-1.wav'
    tgt = Path("../model/label_rle/esuko-LHH-1.npy")
    assert PathManager.data_path(src_1, src_2) == tgt
    src_1, src_2 = "label_rle_delta", 'esuko-LHH-1.wav'
    tgt = Path("../model/label_rle_delta/esuko-LHH-1.npy")
    assert PathManager.data_path(src_1, src_2) == tgt
