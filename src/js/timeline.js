// TIMELINE
var timeline = [];
timeline.push(informed_consent);

// produciotn
timeline.push(production_instructions_practice);
timeline.push(production_practice);
timeline.push(production_instructions);
timeline.push(production);
timeline.push(production_end);

// produciotn
timeline.push(axb_instructions_practice);
timeline.push(axb_practice);
timeline.push(axb_instructions);
timeline.push(axb);
timeline.push(axb_end);

// categorize

jsPsych.init({
    timeline: timeline,
    // on_finish: function(){
    //     jsPsych.data.displayData();
    // }
});
