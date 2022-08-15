function addOptionToSelect(id_select, value, text){
    $('#' + id_select).append($('<option>', {
        value: value,
        text: text
    }));
}

function generateAttributeOptionForSelect(type, is_selected=false){
    if(is_selected){
        return '<option value="' + type + '" selected>' + type + '</option>';
    } else{
        return '<option value="' + type + '">' + type + '</option>';
    }
}

function getValuesFromInputs(inputs=[]){
    var values = [];
    if(inputs.length > 0) {
        for (var i = 0; i < inputs.length; i++) {
            values.push(inputs[i].value);
        }
    }
    return values;
}

function createAttributeInput(div, name='', type='String'){
    var list_types = ["String", "Integer", "Float", "Boolean", "Datetime", "Time"];
    if(list_types.indexOf(type) == -1){
        type = 'String';
    }

    var type_string = generateAttributeOptionForSelect("String", type == "String");
    var type_integer = generateAttributeOptionForSelect("Integer", type == "Integer");
    var type_float = generateAttributeOptionForSelect("Float", type == "Float");
    var type_boolean = generateAttributeOptionForSelect("Boolean", type == "Boolean");
    var type_datetime = generateAttributeOptionForSelect("Datetime", type == "Datetime");
    var type_time = generateAttributeOptionForSelect("Time", type == "Time");

    div.append('<div class="row my-2">' +
        '<div class="col-5"><input type="text" class="attribute_name_input form-control" value="' + name + '"></div>' +
        '<div class="col-5">' +
        '<select class="attribute_type_input form-select">' +
        type_string +
        type_integer +
        type_float +
        type_boolean +
        type_datetime +
        type_time +
        '</select>' +
        '</div>' +
        '<div class="col-2"><button type="button" class="remove_attribute_btn btn btn-danger" onclick="this.parentElement.parentElement.remove();"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill" viewBox="0 0 16 16">\n' +
        '<path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>\n' +
        '</svg>' +
        '</button></div>' +
        '</div>');
}