var timeline = [];
// 1. informed concent 
// 1. instructions_prod
// 1. practice
// 1. trial
// 1. thank you

// https://www.jspsych.org/plugins/jspsych-external-html/

// TODO: オンラインに載せるときは以下も実行
// var check_consent = function(elem) {
//   if (document.getElementById('consent_checkbox').checked) {
//     return true;
//   }
//   else {
//     alert("同意して実験に参加していただける場合はチェックボックスをクリックしてください。");
//     return false;
//   }
//   return false;
// };
// var informed_consent = {
//   type:'external-html',
//   url: "informed_consent.html",
//   cont_btn: "start",
//   check_fn: check_consent
// };
// timeline.push(informed_consent);

var instructions_prod = {
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
timeline.push(instructions_prod);

// このリストを回す
var record = {
    type: 'html-audio-response_modified',
    stimulus: jsPsych.timelineVariable('read'),
    prompt: `<br>
    標準語で上の単語を2回読み上げたらspaceキーを押してください。<br>
    再生ボタンを押して確認し、上手く録音できた場合は Sounds good! で次に進み、<br>
    上手く録音できなかった場合は Retry を押してください。<br>
    ※丸が赤で満たされている時、録音しています。
    `, 
    buffer_length: 60000,
    manually_end_recording_key: ['space'],
    data: {
        item_id: jsPsych.timelineVariable('item_id'),
        read:  jsPsych.timelineVariable('read'),
    },
    on_finish: function(data){
      data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_response);
    },
};
var practice_prod_list = [
  { read: "銀河", item_id: "-1"},
  { read: "アップル", item_id: "-2"},
];
var practice_prod = {
  timeline: [record],
  timeline_variables: practice_prod_list
}
timeline.push(practice_prod);

// REPLACE 
var target_prod_list = [prod_list_to_be_replaced];
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
