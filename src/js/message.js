var form_trial = {
  type: 'survey-html-form',
  preamble: '<p> 実験者から伝えられた4桁の数字をペーストしてください。</p>',
  html: '<p><input name="subject_id" type="text"/></p>'
};

var welcome = {
    type: "html-keyboard-response",
    stimulus: `<p>実験にご参加ありがとうございます。<br>
               スペースキーを押すと実験の説明に移ります。</p>`
};

var thankyou = {
    type: "html-keyboard-response",
    stimulus: `<p>実験にご参加ありがとうございました。<br>
               これにて実験は終了です。スペースキーを押すと画面が空白にったら
               完了ですのでブラウザを閉じてください。
               ご協力ありがとうございました。
               </p>`
};
