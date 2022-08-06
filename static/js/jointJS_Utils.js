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