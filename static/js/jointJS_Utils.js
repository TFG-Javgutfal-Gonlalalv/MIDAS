function random_integer(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function load_box(graph, name, pos_x, pos_y, attributes=[]){
    var rect = new joint.shapes.standard.Rectangle();

    var cell_height = 60;

    var class_text = name + "\n--------------------\n";
    for(var i = 0; i < attributes.length; i++){
        if(i == attributes.length - 1){
            class_text += attributes[i];
        } else{
            class_text += attributes[i] + '\n';
        }
    }

    rect.position(pos_x, pos_y);
    rect.resize(150, cell_height + (15 * (attributes.length)));
    rect.attr({
        body: {
            fill: 'white'
        },
        label: {
            text: class_text,
            fill: 'black'
        }
    });
    rect.addTo(graph);

    var boundaryTool = new joint.elementTools.Boundary();
    var removeButton = new joint.elementTools.Remove();

    var toolsView = new joint.dia.ToolsView({
        tools: [
            boundaryTool,
            removeButton
        ]
    });

    var elementView = rect.findView(paper);
    elementView.addTools(toolsView);
    elementView.hideTools();

    return rect;
}

function load_link(graph, rect1, rect2, label){
    var link = new joint.shapes.standard.Link();
    link.source(rect1);
    link.target(rect2);
    link.attr({
        line: {
            stroke: 'blue',
            strokeWidth: 1,
            sourceMarker: {
                'type': 'path',
                'stroke': 'black',
                'd': 'M 0 0 0 0 0 0 Z'
            },
            targetMarker: {
                'type': 'path',
                'stroke': 'black',
                'd': 'M 0 0 0 0 0 0 Z'
            }
        }
    });
    link.labels([{
        attrs: {
            text: {
                text: label
            }
        }
    }]);
    link.addTo(graph);

    return link;
}

function createLink(graph, class_name_1, class_name_2, mult_1, mult_2){
    if(!$('#new_link_error_msg').hasClass('d-none')){
        $('#new_link_error_msg').addClass('d-none');
    }
    if(!(class_name_2 == undefined || class_name_2 == null || class_name_2 === '') &&
        !(class_name_1 == undefined || class_name_1 == null || class_name_1 === '') &&
        !(mult_1 == undefined || mult_1 == null || mult_1 === '') &&
        !(mult_2 == undefined || mult_2 == null || mult_2 === '')){
        var label = class_name_1 + '_' + mult_1 + '---' + class_name_2 + '_' + mult_2;
        load_link(graph, window[class_name_1], window[class_name_2], label);
        $('#newLinksModal').modal('hide');
    } else {
        $('#new_link_error_msg').removeClass('d-none');
    }
}

function updateClass(graph, cell_id, new_class_name){
    if(!(new_class_name == undefined || new_class_name == null || new_class_name === '')){
        var cell_to_update = graph.getCell(cell_id);
        new_class_name = validate_and_correct_class_name(graph, new_class_name);
        // console.log(cell_to_update);
        cell_to_update.attr({text: {
            text: new_class_name + "\n--------------------\n" },
            label: { text: new_class_name + "\n--------------------\n"
        }});
        window[new_class_name] = cell_to_update;
    }
}

function updateLink(graph, mult_1, mult_2){
    if(!(mult_1 == undefined || mult_1 == null || mult_1 === '') && !(mult_2 == undefined || mult_2 == null || mult_2 === '')){
        var link_to_update = window["editing_link"];

        var class_1 = graph.getCell(link_to_update.attributes.source.id).attributes.attrs.label.text.split("\n--------------------\n")[0];
        var class_2 = graph.getCell(link_to_update.attributes.target.id).attributes.attrs.label.text.split("\n--------------------\n")[0];

        link_to_update.label(0, { attrs: { text: { text: class_1 + '_' + mult_1 + '---' + class_2 + '_' + mult_2 } } });
    }
}

function deleteLink(graph, link){
    link.remove();
}

function validate_and_correct_class_name(graph, class_name){
    var graph_json = graph.toJSON();

    var class_in_graph = [];
    for(var i = 0; i < graph_json["cells"].length; i++){
        if(graph_json["cells"][i]["type"] === "standard.Rectangle"){
            class_in_graph.push(graph_json["cells"][i]["attrs"]["label"]["text"].split('\n--------------------\n')[0]);
        }
    }

    var contains_name = true;
    while(contains_name){
        if(class_in_graph.indexOf(class_name) == -1){
            contains_name = false;
        } else {
            class_name += "_copy";
        }
    }

    return class_name;
}