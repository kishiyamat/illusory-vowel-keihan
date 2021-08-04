var cat_instructions_practice = {
  type: "html-keyboard-response",
  choices: [' '],
  stimulus: `
    <p>　
    次の実験では聞いてもらった音が表記（ひらがな）にどの程度一致しているかを
    1--7段階で評価してもらいます。
    静かな環境で、可能な場合はイヤホンなどの装着をお願いいたします。
    スペースキーを押すと練習課題を2問呈示いたします。
    </p>
  `,
};
  
// Difine stimuli
var cat_practice_stimuli = [
    {item_id: -1, task: "cat-practice", audio: "eSupo.wav", cond_str: "bu"},
    {item_id: -2, task: "cat-practice", audio: "eSupo.wav", cond_str: "bi"},
];
var scale = [ "1", "2", "3", "4", "5", "6", "7"];

//Define Procedure for AXB
var fixation = {
    type: 'html-keyboard-response',
    stimulus: '<div style="font-size:60px;">+</div>',
    choices: jsPsych.NO_KEYS,
    trial_duration: 1000,
};
var cat_presentation = {
    type: 'audio-keyboard-response',
    stimulus: jsPsych.timelineVariable('audio'),
    choices: jsPsych.NO_KEYS,
    trial_ends_after_audio: true,
};
var cat_question_practice = {
    type: 'html-button-response',
    stimulus: '<p></p>',
    choices: ['えしゅぽ', 'えしゅぼ', 'えしぽ', 'えしぼ'], // 文字の大きさに注意
    prompt: "<p>どの表記に近いですか？</p>",
data: {
    task: "cat",
    type: "target",  // filler--target
    item_id: jsPsych.timelineVariable('item_id'), // 想定通りかチェック
},
};
var cat_question = {
    type: 'html-button-response',
    stimulus: '<p></p>',
    choices: ['えすぽ', 'えずぼ', 'えくと', 'えぐど', 'えぷそ', 'えぶぞ', 'えつこ', 'えづご'],
    prompt: "<p>どの表記に近いですか？</p>",
    data: {
        task: "cat",
        type: "target",  // filler--target
        item_id: jsPsych.timelineVariable('item_id'), // 想定通りかチェック
    },
};
var rate = {
    type: 'survey-likert',
    questions: [ {prompt: "聞いた音声は選んだ表記として適切ですか？<br>1: 全く適切でない<br>7: 極めて適切", labels: scale} ],
    data: {
        task: "rate",
        type: "target",  // filler--target
        item_id: jsPsych.timelineVariable('item_id'), // 想定通りかチェック
    },
};

//Practice
var cat_practice = {
    timeline: [fixation, cat_presentation, cat_question_practice, rate],
    timeline_variables: practice_stimuli
}
timeline.push(practice_procedure);

var cat_instructions = {
    type: "html-keyboard-response",
    choices: [' '],
    stimulus: `
        以上で練習問題は終わりです。スペースキーの押下に対応して本番の呈示を開始いたします。</p>
    `,
};

var cat_list = jsPsych.randomization.repeat(cat_list, 1);
var cat = {
    timeline: [fixation, cat_presentation, cat_question, rate],
    timeline_variables: cat_list  // js で定義している
}

var cat_end = {
type: "html-keyboard-response",
  choices: [' '],
stimulus: `
    <p>
    分類課題はこれで終了となります。
    スペースキーを押して次に進んでください。
    </p>
`,
};
