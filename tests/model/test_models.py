from model.models import Model
import pandas as pd
import numpy as np


def test_df2xy():
    """[summary]
            X: (n_cluster, n_sample, n_dim)  # 一番外はList
                [
                    [
                        [1, 0],
                        [1, 0],
                        [1, 0],],
                    [
                        [1, 0],
                        [1, 0],],
                    :
                ]
            y: (n_cluster, n_sample)
                [[y, y, y], [y, y],...]

    Args:
        df (pd.DataFrame): [description]
    """
    src = pd.DataFrame(dict(rle_cluster=[0, 0, 0, 1, 1],
                            stimuli=[0, 0, 0, 0, 0],
                            semitone=[1, 1, 1, 1, 1],
                            silent=[0, 0, 0, 0, 0],
                            rle_label=[0, 0, 0, 0, 0],))

    model = Model(
        subj_idx=0,
        tokyo_kinki_ratio=1,
        use_semitone=True,
        use_duration=True,
        use_transition=True,
        use_pi=True,
        train_ratio=0.5,
        tmat_noise_ratio=0.5,
    )

    res_x, res_y = model.df2xy(src)
    tgt_x = [np.array([[1, 0],
                       [1, 0],
                       [1, 0], ]),
             np.array([[1, 0],
                       [1, 0], ],)]
    tgt_y = [np.array([0, 0, 0]), np.array([0, 0])]
    assert sum([res.shape == tgt.shape for res, tgt in zip(res_x, tgt_x)])
    assert sum([res.shape == tgt.shape for res, tgt in zip(res_y, tgt_y)])
