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
var practice_record = {
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
  timeline: [practice_record],
  timeline_variables: practice_prod_list
}
timeline.push(practice_prod);

var target_prod_list = [{'id': 1, 'kanji': '北上'},{'id': 2, 'kanji': '効き目'},{'id': 3, 'kanji': 'くたびれる'},{'id': 4, 'kanji': '括る'},{'id': 5, 'kanji': '地下'},{'id': 6, 'kanji': '竹輪'},{'id': 7, 'kanji': 'お使い'},{'id': 8, 'kanji': '付き合い'},{'id': 9, 'kanji': '市会'},{'id': 10, 'kanji': '意識'},{'id': 11, 'kanji': '双子'},{'id': 12, 'kanji': '衣服'},{'id': 13, 'kanji': '空き地'},{'id': 14, 'kanji': '狐'},{'id': 15, 'kanji': '唇'},{'id': 16, 'kanji': '退屈'},{'id': 17, 'kanji': '父'},{'id': 18, 'kanji': '秩序'},{'id': 19, 'kanji': '土'},{'id': 20, 'kanji': '五つ'},{'id': 21, 'kanji': '七五'},{'id': 22, 'kanji': '質問'},{'id': 23, 'kanji': 'スチーム'},{'id': 24, 'kanji': '普通'},{'id': 25, 'kanji': '既成'},{'id': 26, 'kanji': '着過ぎる'},{'id': 27, 'kanji': '鎖'},{'id': 28, 'kanji': '薬'},{'id': 29, 'kanji': 'ご馳走'},{'id': 30, 'kanji': '致死量'},{'id': 31, 'kanji': '初日の出'},{'id': 32, 'kanji': '写し'},{'id': 33, 'kanji': '視察'},{'id': 34, 'kanji': '獅子舞'},{'id': 35, 'kanji': '不正'},{'id': 36, 'kanji': '不思議'},{'id': 37, 'kanji': '怪我'},{'id': 38, 'kanji': '毛嫌い'},{'id': 39, 'kanji': '心'},{'id': 40, 'kanji': '小瓶'},{'id': 41, 'kanji': 'チェコ'},{'id': 42, 'kanji': 'チェキア'},{'id': 43, 'kanji': 'おちょこ'},{'id': 44, 'kanji': '貯金'},{'id': 45, 'kanji': 'セブ'},{'id': 46, 'kanji': '背取り'},{'id': 47, 'kanji': 'ソビエト'},{'id': 48, 'kanji': '蕎麦'},{'id': 49, 'kanji': '蹴散らす'},{'id': 50, 'kanji': '鉄'},{'id': 51, 'kanji': 'こち亀'},{'id': 52, 'kanji': 'コチュジャン'},{'id': 53, 'kanji': 'チェチェン'},{'id': 54, 'kanji': 'じぇじぇ'},{'id': 55, 'kanji': '貯蓄'},{'id': 56, 'kanji': 'ジョジョ'},{'id': 57, 'kanji': 'へちま'},{'id': 58, 'kanji': '説明'},{'id': 59, 'kanji': '措置'},{'id': 60, 'kanji': 'ほつれ'},{'id': 61, 'kanji': 'テスト'},{'id': 62, 'kanji': '手相'},{'id': 63, 'kanji': '都市'},{'id': 64, 'kanji': 'コスト'},{'id': 65, 'kanji': 'チェス'},{'id': 66, 'kanji': 'チェシャ猫'},{'id': 67, 'kanji': '貯水'},{'id': 68, 'kanji': '著者'},{'id': 69, 'kanji': 'へそ曲がり'},{'id': 70, 'kanji': 'せせらぎ'},{'id': 71, 'kanji': '細さ'},{'id': 72, 'kanji': '舗装'}]; // ここをreplace
var practice_prod = {
  timeline: [practice_record],
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

// TODO: 
//timeline.push({
//    type: 'html-audio-response_modified',
//    stimulus: '刺激',
//    prompt: "指示", 
//    buffer_length: 10000,
//    manually_end_recording_key: ['space'],
//});

jsPsych.init({
    timeline: timeline,
    // on_finish: function(){
    //     jsPsych.data.displayData();
    // }
});
