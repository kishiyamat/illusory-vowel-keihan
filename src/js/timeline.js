// 一番最後でいい
var timeline = [];
timeline.push(informed_consent);

// produciotn
timeline.push(production_instructions_practice);
timeline.push(production_practice);
timeline.push(production_instructions);
timeline.push(production);
timeline.push(production_end);

jsPsych.init({
    timeline: timeline,
    // on_finish: function(){
    //     jsPsych.data.displayData();
    // }
});
