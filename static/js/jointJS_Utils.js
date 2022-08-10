function random_integer(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function load_box(graph, name, pos_x, pos_y){
    var rect = new joint.shapes.standard.Rectangle();
    rect.position(pos_x, pos_y);
    rect.resize(150, 40);
    rect.attr({
        body: {
            fill: 'white'
        },
        label: {
            text: name,
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

function updateClass(graph, cell_id, new_class_name){
    if(!(new_class_name == undefined || new_class_name == null || new_class_name === '')){
        var cell_to_update = graph.getCell(cell_id);
        new_class_name = validate_and_correct_class_name(graph, new_class_name);
        // console.log(cell_to_update);
        cell_to_update.attr({text: { text: new_class_name }, label: { text: new_class_name }});
    }
}

function validate_and_correct_class_name(graph, class_name){
    var graph_json = graph.toJSON();
    for(var i = 0; i < graph_json["cells"].length; i++){
        if((graph_json["cells"][i]["type"] === "standard.Rectangle") && (graph_json["cells"][i]["attrs"]["label"]["text"] === class_name)){
            class_name += "_copy";
        }
    }
    return class_name;
}