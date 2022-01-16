# illusory-vowel-keihan

* 知覚実験は6分程度

## 実験の作り方

### 産出・知覚実験

1. srcに言ってmake jsする
    * ※: 追加の作業として、
      CWのデータは年齢を聞き、またクラウドワークスのidを入力してもらっている。
1. cognition.run にアップロードする
    1. css, audioのmodをアップロード > External JS/CSS
    1. 音源 > Stimuli
    1. informed.html > Stimuli
1. URLを発行

### 追跡調査

1. Google Form に作成 

最初にドラフトを作成してもらい、
共同研究者からのコメントをもらって編集していく。

## 実施

1. 被験者募集
1. 以下の文面を協力者の方に送信

<name>様

突然のご連絡失礼いたします。東京大学大学院博士課程の岸山健と申します。
この度は幼児教育科学研究所の曽根様のご紹介をいただき、<name>様に実験実施へのご協力をたまわりたくご連絡いたしました。

私が所属している研究室では人の音声産出・知覚のプロセスを検証しており、
今回は特定の地域にお住まいの方に音声の産出・知覚の実験を実施予定です。
ご協力していただきたい点は以下の3点です。

1. 被験者募集
1. 重複のない被験者idの割り振り
1. 実験実施

もしご検討いただける場合、曽根様が実験実施説明のLINEグループをご共有してくださるとのことです。
上記の内容の詳細をそちらでご説明させていただきたく存じます。

ご多忙のところ大変恐縮ですが、どうぞよろしくお願いいたします。

東京大学大学院 総合文化研究科
言語情報科学専攻 博士後期課程
岸山健

1. 協力をいただける場合、実験の説明

<name>様、この度は実験へのご協力ありがとうございます。
先日申し上げた 1. 被験者募集 2. 重複のない被験者idの割り振り 3. 実験実施 の
それぞれに付いて説明させていただきます。

本実験では関東(東京方言)と関西(近畿方言)にお住まいの方を対象に、
音声の産出と知覚の実験に参加していただきます。
そこでまずは4名、関西にお住まいの方のご協力をたまわりたく、
被験者を募集していただきます。

次に被験者idの割り振りですが、東京方言話者は0000--0999、
近畿方言話者は1000--1999 の 4桁を重複なく割り振ります。
途中でずれてしまっても問題ございません。

最後に実験実施についてですが、実験に参加してくださる方に
以下のURLと、上で割り振った被験者idをお伝えください。
実験の内容と必要な時間は最初のページに記述してありますが、
静かな環境で参加していただき、
標準語のアクセントで産出実験に参加していただくようご依頼ください。

https://qgmpzq3aul.cognition.run

どうぞよろしくお願いいたします。

### 被験者番号

東京方言話者は0000番代、
近畿方言話者は1000番代、
パイロットは2000↑で実験を実施します。

ただ、kinkiやtokyoの情報はあるので、そちらを参考にしたほうが早そう。
年齢とかでもだいぶ変わるかもだし。年齢が20--としたのはまずかったかなぁ。
40--あたりをターゲットにして追加募集をしても良いかも知れない。

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
- pip install --upgrade cython
- pip install git+https://github.com/kishiyamat/hsmmlearn.git
    - multivariateがmergeされるまで
- pip install numba # librosaが依存; numpyが厳しい
- pip install librosa

## 分析

- データを取得
  - crowdworks と soneさんでルートを分けているので、
    `/Users/takeshi.kishiyama/illusory-vowel-keihan/results/csv` に
    以下のファイルを配置
    - `illusory-vowel-keihan.csv`
    - `illusory-vowel-keihan-cw.csv`
- 分析ファイルの実行
  - アノテーション
  - トーンの知覚
    - pitch-delta: tokyo preference の分析
    - pitch-delta: そもそもの正答率
  - 異音の弁別
    - allophone: 

```
```

### アノテーション

- 指定区間が無声化しているかしていないか
- praat で vocing のmsを記録
    - msが短い場合、あるないのしきい値を決めるのはエラーのもと
    - text grid を作った方が早いかもしれないが、まずは速さを優先
- ゆっくり読んでも無声化しない人はいる。
  ただ、多分本人の中では無声化しないで呼んでいるつもりなのかも知れない。
  在住歴と無声化のデータだけでも回収・報告する。
  東京で無声化しないケースもある。
- もしかしたらもう無声化するのかも。
    - 一旦、年齢でフィルターしてみる？
    - いや、普通にバリエーションはある
    - 逆に年齢を絞ると年齢が交絡する。
    - 近畿に長い人に絞ると、たしかに非無声化のサンプルがあった。上から進めていくのが吉
    - アノテーションは思ったより揺れなさそうなので、進められるぶんはどんどんすすめる
- 名物を「めいぶつ」と呼んでいるのはちょっとあやしい
- 順序のデータが約にたつかもしれないので、あとでマージする
- モーラの数、HLのパターン、位置が違う。

## 募集文面

### 産出・知覚実験

### 追跡調査

### ライブラリー

```
pip install praat-parselmouth
```

## シミュレーション

- HSMMでモデリング


