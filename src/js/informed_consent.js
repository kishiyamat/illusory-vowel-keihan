// informed consent
// https://www.jspsych.org/plugins/jspsych-external-html/
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
