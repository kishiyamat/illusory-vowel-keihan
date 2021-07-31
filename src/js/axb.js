var axb_instructions_practice = {
  type: "html-keyboard-response",
  stimulus: `
    <p>キーを押すと練習課題に移ってしまうので、
    以下のお願いを全て読んでからキーを押してください。</p>
    <p>この実験の各課題では A->X->B という順序で
    3つの音を聞いてもらいます。
    そしてX、つまり2つ目の音が似ているのはAかBかを
    答えていただきます。</p>
    <p>キーを押すと練習課題を2問呈示いたします。
    </p>
  `,
};

//Define Procedure for AXB
var fixation = {
  type: 'html-keyboard-response',
  stimulus: '<div style="font-size:60px;">+</div>',
  choices: jsPsych.NO_KEYS,
  trial_duration: 1000,
}
var trial_a = {
    type: 'audio-keyboard-response',
    stimulus: jsPsych.timelineVariable('a'),
    choices: jsPsych.NO_KEYS,
    trial_ends_after_audio: true,
    post_trial_gap: 200,
};
var trial_x = {
    type: 'audio-keyboard-response',
    stimulus: jsPsych.timelineVariable('x'),
    choices: jsPsych.NO_KEYS,
    trial_ends_after_audio: true,
    post_trial_gap: 200,
};
var trial_b = {
    type: 'audio-keyboard-response',
    stimulus: jsPsych.timelineVariable('b'),
    choices: jsPsych.NO_KEYS,
    trial_ends_after_audio: true,
};
var question = {
    type: 'html-keyboard-response',
    stimulus: '音声呈示は A->X->B の順でした。',
    choices: ['a', 'b'],
    prompt: "<p>Xの音がAと同じなら'a'を押し、Bと同じなら'b'を押してください。</p>",
    data: {
        index: jsPsych.timelineVariable('index'),
        latin: jsPsych.timelineVariable('latin'),
        task:  jsPsych.timelineVariable('task'),
        c1_duration:  jsPsych.timelineVariable('c1_duration'),
        cond_context:  jsPsych.timelineVariable('cond_context'),
        cond_prev:  jsPsych.timelineVariable('cond_prev'),
        token_sequence: jsPsych.timelineVariable('token_sequence'),
        speaker_sequence: jsPsych.timelineVariable('speaker_sequence'),
        correct_response: jsPsych.timelineVariable('correct_response'),
    },
    on_finish: function(data){
      data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    },
};
var feedback = {
    type: 'html-keyboard-response',
    stimulus: function(){
        let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;
        if (last_trial_correct) { return "<p>正解です。</p>"; }
        else { return "<p>不正解です。</p>"; }
    },
    choices: [' '],
    prompt: "次の問題に進む場合はスペースキーを押してください。",
};
var rest = {
    type: 'html-keyboard-response',
    // stimulus: '<p>Running</p>',
    stimulus: function(){
        var fool_proof = "<p>以下のアイテム情報は本来見えるべきではありません。".concat(
                         "もし本実験で見えてしまっている場合はお手数ですが実験実施者にご連絡ください。<p>");
        let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;
        var is_correct = last_trial_correct? "正解<br>":  "不正解<br>";
        var pair = "pair: ".concat(jsPsych.timelineVariable('pair_str'), "<br>");
        var a = "a: ".concat(jsPsych.timelineVariable('a'), "<br>");
        var x = "x: ".concat(jsPsych.timelineVariable('x'), "<br>");
        var b = "b: ".concat(jsPsych.timelineVariable('b'), "<br>");
        return "".concat(fool_proof, pair, is_correct, a, x, b);
    },
    choices: [' '],
    prompt: "次の問題に進む場合はスペースキーを押してください。",
};

//Practice
var practice_stimuli = [
  { a: "32.mp3", x:"33.mp3", b:"33.mp3", cond_str: "b", correct_response: 'b', task: "axb-practice"},
  { a: "33.mp3", x:"33.mp3", b:"32.mp3", cond_str: "a", correct_response: 'a', task: "axb-practice"},
];
var axb_practice = {
  timeline: [fixation, trial_a, trial_x, trial_b, question, feedback],
  timeline_variables: practice_stimuli
}

var axb_instructions = {
  type: "html-keyboard-response",
  stimulus: `
    <p>今流れたものは機械的な音ですが、
    実際に流れる音は3人の人が読み上げる音声です。
    さきほどのものより違いがかなり微細なので、
    注意して聞き分けてみてください。</p>
    <p>また、今の練習課題では回答の正誤を表示しましたが、
    本番では表示しません。</p>
    <p>キーの押下で本番の呈示を開始いたします。</p>
  `,
};

var perception_list = jsPsych.randomization.repeat(perception_list, 1);

var axb = {
  timeline: [fixation, trial_a, trial_x, trial_b, question, rest],
  timeline_variables: perception_list
}

var axb_end = {
  type: "html-keyboard-response",
  stimulus: `
    <p>
    弁別課題はこれで終了となります。
    お好きなキーを押して次に進んでください。
    </p>
  `,
};

