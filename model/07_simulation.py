
# %%
# stimuli列ごとに抜き出して学習させれば良い
import pandas as pd
data = pd.read_csv('artifacts/data.csv')
data.head()
# %%
train_df = data.query("is_train == True")
test_df = data.query("is_train == False")
# %%


class Model:
    def __init__(self, use_semitone: bool, use_duration: bool, use_transition: bool, tokyo_kinki_ratio: float, acoustic="bayes"):
        """[summary]

        Args:
            use_semitone (bool): [特徴量としてsemitoneを利用(被験者の発話ごとに標準化)するか]
            use_duration (bool): [ラベルに持続時間を埋め込むか: HHをH2とするかHHとするか]
            use_transition (bool): [遷移確率を利用するか: P(H->L2)とP(H2->L)を一様とするか]
            tokyo_kinki_ratio (float): [行動実験の要因とされた東京に居住した割合]
        """
        self.use_semitone = use_semitone
        self.use_duration = use_duration
        self.use_transition = use_transition
        self.tokyo_kinki_ratio = tokyo_kinki_ratio  # tokyoの影響は必ず入る
        self.tmat = None  # blend
        self.le = LabelEncoder()
        model = GaussianNB() if acoustic == "bayes" else tree.DecisionTreeClassifier(max_depth=3)
        self.pipe = Pipeline([
            ("impute", SimpleImputer(missing_values=np.nan, strategy='mean')),
            ("model", model),
        ])

    @property
    def tmat_kinki(self):
        # TODO: 後で定義
        # self.use_duration = use_duration に依存
        pass

    @property
    def tmat_tokyo(self):
        # TODO: 後で定義
        # self.use_duration = use_duration に依存
        pass

    def fit(self, df: pd.DataFrame):
        # X has pitch and sil indicator, y is label
        X_list = []
        sil_list = []
        y_list = []
        for _, row in df.groupby("stimuli"):
            X_list.extend(row.semitone if self.use_semitone else row.pitch)
            sil_list.extend(row.silent)
            y_i = row.rle_label if self.use_duration else row.label
            y_list.extend(y_i)
        self._X = np.array([X_list, sil_list]).T
        self._X_scaled = self.pipe[:-1].fit_transform(self._X)
        self._y = self.le.fit_transform(np.array(y_list))
        # Acoustic Model
        self.pipe.fit(self._X, self._y)
        # Duration
        dur_dict = {"label": [], "duration": []}
        cluster_key = "rle_cluster" if self.use_duration else "cluster"
        for _, row in df.groupby(["stimuli", cluster_key]):
            label, *_ = row.rle_label if self.use_duration else row.label
            dur_dict["label"] += [label]
            dur_dict["duration"] += [len(row)]
        self.dur_dict = dur_dict
        # TMAT
        return self

    def draw_features(self):
        label_name = 'semitone' if self.use_duration else "pitch"
        color_name = "rle_label" if self.use_duration else "label"
        df = pd.DataFrame({label_name: self._X_scaled[:, 0],
                           color_name: self.le.inverse_transform(self._y),
                           'silent': self._X[:, 1]})
        p = (ggplot(df, aes(x=label_name, color=color_name, fill=color_name))
             + facet_grid(f"{color_name} ~ silent")
             + geom_histogram()
             + labs(x=label_name, y="count")
             + scale_y_log10()
             )
        return p

    def draw_duration(self):
        duration_df = pd.DataFrame(self.dur_dict)
        p = (ggplot(duration_df, aes(x='duration', color="label", fill="label"))
             + facet_grid(". ~ label")
             + geom_histogram(bins=20)
             + labs(x='duration', y='count')
             )
        return p

    def predict(self):
        # semitoneとかそこらへんもしっかりキャッチする
        # 入力に sil などの nan があることを仮定する。ないことは仮定しない
        # 入力と出力は合わせる
        pass


# %%
model = Model(use_semitone=True,
              use_duration=True,
              use_transition=True,
              tokyo_kinki_ratio=1.0,
              )
model.fit(train_df)
print(model.draw_features())
# model.dur_dict

# %%
clf = model.pipe[-1]
if type(clf) == tree.DecisionTreeClassifier:
    tree.export_graphviz(clf, out_file="artifacts/tree.dot", class_names=model.le.classes_,
                         feature_names=["semitone", "silent"], impurity=False, filled=True)
# %%
trues = []
preds = []
for true, pred in zip(model.le.inverse_transform(model._y), model.le.inverse_transform(model.pipe.predict(model._X_scaled))):
    trues.append(true[0])
    preds.append(pred[0])
    print(true, pred)
# まさかのsemitone使わない方がセグメンタルには性能高そう
# dt: 0.7383720930232558
# nb: 0.7151162790697675
accuracy_score(trues, preds)
# %%
model.le.classes_
# %%
model.pipe.predict_proba(model._X_scaled[-6:])
# %%
print(model.draw_duration())
# %%
duration_df = pd.DataFrame(model.dur_dict)
duration_df.groupby("label").var()
duration_df.groupby("label").mean()
# %%
duration_df

# %%
# Gaussian KDE
# Gaussian Mixture でいいのでは？
# 2くらいでいい
X = duration_df.query("label=='H1'").duration.values.reshape(-1, 1)
# y = model.le.transform(duration_df.label.values)
gm = GaussianMixture(n_components=2)
gm.fit(X)
np.exp(gm.score([[30]]))
# %%
np.exp(gm.score([[15]]))
# %%
gm.predict_proba([[10]])
max_dur = max(X+10)
max_dur
p((y1, y2, y3, y4) | X)
# %%
# %%
# 0とはできない. semitoneの時に別の意味になる。
# nanとはできない. 混合ガウスだから nan はない。
train_df
# p = (ggplot(train_df.fillna(train_df.mean()), aes(x='pitch', color="rle_label", fill="rle_label"))
p = (ggplot(train_df.fillna(train_df.mean()), aes(x='semitone', color="rle_label", fill="rle_label"))
     + facet_grid("rle_label ~ silent")
     + geom_histogram()
     + labs(x='time', y='semitone')
     + scale_y_log10()
     )
print(p)
# p.save(filename='artifacts/tone_by_cluster_rle.png',
#        height=8, width=8, units='cm', dpi=1000)

# %%
use_semitones = [True, False]
use_durations = [True, False]
use_transitions = [True, False]
tokyo_kinki_ratios = np.arange(-1.0, 1.1, 0.5)  # 1を含めて0.5刻みの-1から1 -> len==5
# %%
conditions = itertools.product(
    use_semitones,
    use_durations,
    use_transitions,
    tokyo_kinki_ratios,
)
for use_semitone, use_duration, use_transition, tokyo_kinki_ratio in list(conditions):
    model = Model(use_semitone,
                  use_duration,
                  use_transition,
                  tokyo_kinki_ratio)
    model.fit(train_x, train_y)
    print(model)


# %%
# Appendix
# Semitoneが1あがると半音あがる. toneは2音あがる
# semitone = lambda x: 12 * np.log(x/base) / np.log(2)
# tone = lambda x: 6 * np.log(x/base) / np.log(2)
# https://www.youtube.com/watch?v=QgEInLU92Ls
# 1あがると半音あがる、そんな指標


def tone(pitch, base): return 6 * np.log(pitch/base) / np.log(2),
def semitone(pitch, base): return 12 * np.log(pitch/base) / np.log(2),


do = 130.813
do_sharp = 138.591
re = 146.832
print(tone(re, do))
print(semitone(re, do))

# %%