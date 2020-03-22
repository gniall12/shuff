function shuffle(id, name) {
    $.get("/shuffle", {
        "id": id,
        "name": name
    }, function(data, status) {
        console.log(data);
        console.log(status);
    }, "json")
    .fail(function(data){
        window.location.replace('/error?code=' + data.status + '&message=' + data.responseText);
    });
}