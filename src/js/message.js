var form_trial = {
  type: 'survey-html-form',
  preamble: '<p> 実験者から伝えられた4桁の数字を入力してください。</p>',
  html: '<p><input name="subject_id" type="number"/></p>'
};

var form_tokyo = {
  type: 'survey-html-form',
  preamble: '<p> これまで東京に居住してきた年数を入力して下さい。</p>',
  html: '<p><input name="span_tokyo" type="number"/></p>'
};

var form_kinki = {
  type: 'survey-html-form',
  preamble: '<p> これまで近畿地方に居住してきた年数を入力して下さい。</p>',
  html: '<p><input name="span_kinki" type="number"/></p>'
};

var welcome = {
    type: "html-keyboard-response",
    stimulus: `<p>実験にご参加ありがとうございます。<br>
               スペースキーを押すと実験の説明に移ります。</p>`
};

var thankyou = {
    type: "html-keyboard-response",
    stimulus: `<p>実験にご参加ありがとうございました。<br>
               これにて実験は終了です。スペースキーを押すと画面が空白になったら
               完了ですのでブラウザを閉じてください。
               ご協力ありがとうございました。
               </p>`
};
