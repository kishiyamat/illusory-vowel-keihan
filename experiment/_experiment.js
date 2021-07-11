var timeline = [];
// 1. informed concent 
// 1. instructions_prod
// 1. practice
// 1. trial
// 1. thank you

// https://www.jspsych.org/plugins/jspsych-external-html/

// TODO: オンラインに載せるときは以下も実行
var check_consent = function(elem) {
  if (document.getElementById('consent_checkbox').checked) {
    return true;
  }
  else {
    alert("同意して実験に参加していただける場合はチェックボックスをクリックしてください。");
    return false;
  }
  return false;
};
var informed_consent = {
  type:'external-html',
  url: "informed_consent.html",
  cont_btn: "start",
  check_fn: check_consent
};
timeline.push(informed_consent);

var instructions_practice = {
  type: "html-keyboard-response",
  stimulus: `
    <p>キーを押すと練習課題に移ってしまうので、<br>
    以下のお願いを全て読んでからキーを押してください。<br><br>
    最初の産出実験では、一番上に表示される単語を<br>
    標準語で2回ずつ読み上げていただきます。<br> <br>
    キーを押すと2セットの練習課題に移ります。<br>
    必要に応じてマイクの許可をお願いいたします。</p>
    `,
};
timeline.push(instructions_practice);

// このリストを回す
var record = {
    type: 'html-audio-response_modified',
    stimulus: jsPsych.timelineVariable('read'),
    prompt: `<br>
    大きな声ではっきりと、<br>
    標準語で上の単語を2回読み上げたらspaceキーを押してください。<br>
    再生ボタンを押して確認し、上手く録音できた場合は Sounds good! で次に進み、<br>
    上手く録音できなかった場合は Retry を押してください。<br>
    小さな声しか出せない環境での実施は想定されておらず、<br>
    その後の分析で非常に困りますので場所が不適切な場合は移動をお願いいたします。<br>
    ※丸が赤で満たされている時、録音しています。
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
var practice_prod_list = [
  {type: "production", item_id: -1, read: "銀河", },
  {type: "production", item_id: -2, read: "アップル"},
];
var practice_prod = {
  timeline: [record],
  timeline_variables: practice_prod_list
}
timeline.push(practice_prod);

var instructions_target = {
  type: "html-keyboard-response",
  stimulus: `
    <p>以上で練習は終わりです。もしもう一度練習を希望される場合は<br>
    本画面を閉じてから再度同じURLを開いてください。<br><br>
    キーを押すと2セットの本番の産出課題に移ります。<br>
    丸が赤で満たされているときは録音しています。<br>
    ※途中で間違えて次に進んでしまったとしても、<br>
    そこまで致命的な問題にはなりません。<br>
    </p>
    `,
};
timeline.push(instructions_target);

// REPLACE and randomize
var target_prod_list = [prod_list_to_be_replaced];
var target_prod_list = jsPsych.randomization.repeat(target_prod_list, 1);

var practice_prod = {
  timeline: [record],
  timeline_variables: target_prod_list
}
timeline.push(practice_prod);

var finish_prod = {
  type: "html-keyboard-response",
  stimulus: `
    <p>
    産出課題はこれで終了となります。
    お好きなキーを押して次に進んでください。
    </p>
  `,
};
timeline.push(finish_prod);

jsPsych.init({
    timeline: timeline,
    // on_finish: function(){
    //     jsPsych.data.displayData();
    // }
});
