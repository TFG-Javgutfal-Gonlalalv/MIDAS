function addOptionToSelect(id_select, value, text){
    $('#' + id_select).append($('<option>', {
        value: value,
        text: text
    }));
}