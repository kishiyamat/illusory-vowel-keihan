# illusory-vowel-keihan

* 知覚実験は6分程度

## 実験の作り方

1. srcに言ってmake jsする
1. cognition.run にアップロードする
    1. css, audioのmodをアップロード > External JS/CSS
    1. 音源 > Stimuli
    1. informed.html > Stimuli
1. URLを発行

## 実施

### 被験者番号

東京方言話者は0000番代、
近畿方言話者は1000番代、
パイロットは2000↑で実験を実施します。

## セットアップ

元来jsPsychのリスト管理は面倒くさい。
もうpythonの中にjsを書くか...。

### ローカル

1. `src/` に `jspsych-html-audio-response_modified.js` を配置
1. `src/` に `jspsych-6.3.1` を配置

### リモート

1. `src/` に `jspsych-html-audio-response_modified.js` をアップロード
1. 音声をアップロード

assert を上手く使って想定内の挙動であることを保証し続ける。
一つのpyですべて変換させる。

### ソフトウェア

- brew install git-lfs

## 分析



### ライブラリー

```
pip install praat-parselmouth
```

