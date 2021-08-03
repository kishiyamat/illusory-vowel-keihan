// PRODUCTION EXPERIMENT
var production_instructions_practice = {
  type: "html-keyboard-response",
  stimulus: `
    <p>スペースキーを押すと練習課題に移ってしまうので、
    <u>以下のお願いを全て読んでから</u>キーを押してください。</p>
    <p>この産出実験では、一番上に表示される単語を
    大きな声、標準語で3回ずつ読み上げていただきます。
    マイクへのアクセスが要求さればた場合は許可し、
    静かな環境での実施をお願いいたします。</p>
    <p>スペースキーを押すと練習課題を2問呈示いたします。</p>
    `,
};

var record = {
    type: 'html-audio-response_modified',
    stimulus: jsPsych.timelineVariable('read'),
    prompt: `<p>上の単語を大きな声で標準語で3回読み上げたらスペースキーを押してください。</p>
    <p>再生ボタンを押して確認し、上手く録音できた場合は「次へ進む」、
    上手く録音できなかった場合は「やり直す」を押してください。</p>
    <p> ※丸が赤で満たされている時は録音中です。 </p>
    `, 
    buffer_length: 60000,
    manually_end_recording_key: ['space'],
    data: {
        type:  jsPsych.timelineVariable('type'),
        item_id: jsPsych.timelineVariable('item_id'),
        read:  jsPsych.timelineVariable('read'),
    },
    on_finish: function(data){
      data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    },
};
var production_list_practice = [
  {type: "production", item_id: -1, read: "銀河", },
  {type: "production", item_id: -2, read: "アップル"},
];
var production_practice = {
  timeline: [record],
  timeline_variables: production_list_practice
}

var production_instructions = {
  type: "html-keyboard-response",
  stimulus: `
    <p>以上で練習は終わりです。スペースキーを押すと2セットの本番の産出課題に移ります。</p>
    `,
};

var production_list = jsPsych.randomization.repeat(production_list, 1);
var production = {
  timeline: [record],
  timeline_variables: production_list
}

var production_end = {
  type: "html-keyboard-response",
  choices: [' '],
  stimulus: `
    <p>
    産出課題はこれで終了となります。スペースキーを押して次に進んでください。
    </p>
  `,
};
