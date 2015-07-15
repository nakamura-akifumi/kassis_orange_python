function build_parameter(key, obj) {
    var current_location = location.href;

    var params = current_location.split('&');
    var url = '';
    for (var i = 0; i < params.length; i++) {
        if (params[i].lastIndexOf(key + '=', 0) != 0) {
            if (url != '') {
                url = url + '&';
            }
            url = url + params[i];
        }
    }
    if (obj.value == undefined) {
        url = url + '&' + key + '=' + obj;
    } else {
        url = url + '&' + key + '=' + obj.value;
    }
    return url;
}
function sortChange(obj) {
    location.href = build_parameter("o2", obj)

    return true;
}
function perPageChange(obj) {
    location.href = build_parameter("o1", obj)

    return true;
}
function pageChange(obj) {
    location.href = build_parameter("p", obj)

    return true;
}