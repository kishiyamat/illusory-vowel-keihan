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

// REPLACE and randomize
var target_prod_list = [{'type': 'production', 'item_id': 1, 'read': '北上 (きたかみ)'},{'type': 'production', 'item_id': 2, 'read': '効き目 (ききめ)'},{'type': 'production', 'item_id': 3, 'read': 'くたびれる (くたびれる)'},{'type': 'production', 'item_id': 4, 'read': '括る (くくる)'},{'type': 'production', 'item_id': 5, 'read': '地下 (ちか)'},{'type': 'production', 'item_id': 6, 'read': '竹輪 (ちくわ)'},{'type': 'production', 'item_id': 7, 'read': 'お使い (おつかい)'},{'type': 'production', 'item_id': 8, 'read': '付き合い (つきあい)'},{'type': 'production', 'item_id': 9, 'read': '市会 (しかい)'},{'type': 'production', 'item_id': 10, 'read': '意識 (いしき)'},{'type': 'production', 'item_id': 11, 'read': '双子 (ふたご)'},{'type': 'production', 'item_id': 12, 'read': '衣服 (いふく)'},{'type': 'production', 'item_id': 13, 'read': '空き地 (あきち)'},{'type': 'production', 'item_id': 14, 'read': '狐 (きつね)'},{'type': 'production', 'item_id': 15, 'read': '唇 (くちびる)'},{'type': 'production', 'item_id': 16, 'read': '退屈 (たいくつ)'},{'type': 'production', 'item_id': 17, 'read': '父 (ちち)'},{'type': 'production', 'item_id': 18, 'read': '秩序 (ちつじょ)'},{'type': 'production', 'item_id': 19, 'read': '土 (つち)'},{'type': 'production', 'item_id': 20, 'read': '五つ (いつつ)'},{'type': 'production', 'item_id': 21, 'read': '七五 (しちご)'},{'type': 'production', 'item_id': 22, 'read': '質問 (しつもん)'},{'type': 'production', 'item_id': 23, 'read': 'スチーム (すちーむ)'},{'type': 'production', 'item_id': 24, 'read': '普通 (ふつう)'},{'type': 'production', 'item_id': 25, 'read': '既成 (きせい)'},{'type': 'production', 'item_id': 26, 'read': '着過ぎる (きすぎる)'},{'type': 'production', 'item_id': 27, 'read': '鎖 (くさり)'},{'type': 'production', 'item_id': 28, 'read': '薬 (くすり)'},{'type': 'production', 'item_id': 29, 'read': 'ご馳走 (ごちそう)'},{'type': 'production', 'item_id': 30, 'read': '致死量 (ちしりょう)'},{'type': 'production', 'item_id': 31, 'read': '初日の出 (はつひので)'},{'type': 'production', 'item_id': 32, 'read': '写し (うつし)'},{'type': 'production', 'item_id': 33, 'read': '視察 (しさつ)'},{'type': 'production', 'item_id': 34, 'read': '獅子舞 (ししまい)'},{'type': 'production', 'item_id': 35, 'read': '不正 (ふせい)'},{'type': 'production', 'item_id': 36, 'read': '不思議 (ふしぎ)'},{'type': 'production', 'item_id': 37, 'read': '怪我 (けが)'},{'type': 'production', 'item_id': 38, 'read': '毛嫌い (けぎらい)'},{'type': 'production', 'item_id': 39, 'read': '心 (こころ)'},{'type': 'production', 'item_id': 40, 'read': '小瓶 (こびん)'},{'type': 'production', 'item_id': 41, 'read': 'チェコ (ちぇこ)'},{'type': 'production', 'item_id': 42, 'read': 'チェキア (ちぇきあ)'},{'type': 'production', 'item_id': 43, 'read': 'おちょこ (おちょこ)'},{'type': 'production', 'item_id': 44, 'read': '貯金 (ちょきん)'},{'type': 'production', 'item_id': 45, 'read': 'セブ (せぶ)'},{'type': 'production', 'item_id': 46, 'read': '背取り (せどり)'},{'type': 'production', 'item_id': 47, 'read': 'ソビエト (そびえと)'},{'type': 'production', 'item_id': 48, 'read': '蕎麦 (そば)'},{'type': 'production', 'item_id': 49, 'read': '蹴散らす (けちらす)'},{'type': 'production', 'item_id': 50, 'read': '鉄 (てつ)'},{'type': 'production', 'item_id': 51, 'read': 'こち亀 (こちかめ)'},{'type': 'production', 'item_id': 52, 'read': 'コチュジャン (こちゅじゃん)'},{'type': 'production', 'item_id': 53, 'read': 'チェチェン (ちぇちぇん)'},{'type': 'production', 'item_id': 54, 'read': 'じぇじぇ (じぇじぇ)'},{'type': 'production', 'item_id': 55, 'read': '貯蓄 (ちょちく)'},{'type': 'production', 'item_id': 56, 'read': 'ジョジョ (じょじょ)'},{'type': 'production', 'item_id': 57, 'read': 'へちま (へちま)'},{'type': 'production', 'item_id': 58, 'read': '説明 (せつめい)'},{'type': 'production', 'item_id': 59, 'read': '措置 (そち)'},{'type': 'production', 'item_id': 60, 'read': 'ほつれ (ほつれ)'},{'type': 'production', 'item_id': 61, 'read': 'テスト (てすと)'},{'type': 'production', 'item_id': 62, 'read': '手相 (てそう)'},{'type': 'production', 'item_id': 63, 'read': '都市 (とし)'},{'type': 'production', 'item_id': 64, 'read': 'コスト (こすと)'},{'type': 'production', 'item_id': 65, 'read': 'チェス (ちぇす)'},{'type': 'production', 'item_id': 66, 'read': 'チェシャ猫 (ちぇしゃねこ)'},{'type': 'production', 'item_id': 67, 'read': '貯水 (ちょすい)'},{'type': 'production', 'item_id': 68, 'read': '著者 (ちょしゃ)'},{'type': 'production', 'item_id': 69, 'read': 'へそ曲がり (へそまがり)'},{'type': 'production', 'item_id': 70, 'read': 'せせらぎ (せせらぎ)'},{'type': 'production', 'item_id': 71, 'read': '細さ (ほそさ)'},{'type': 'production', 'item_id': 72, 'read': '舗装 (ほそう)'}];
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
