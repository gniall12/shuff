function shuffle(id, name) {
    var playlistElement = document.getElementById(id);
    playlistElement.innerText = "Loading...";
    playlistElement.style.opacity = "0.5";
    playlistElement.disabled = true;
    $.get("/shuffle", {
        "id": id,
        "name": name
    }, function(data, status) {
        console.log(data);
        console.log(status);
    }, "json")
    .fail(function(data){
        window.location.replace('/error?code=' + data.status + '&message=' + data.responseText);
    })
    .always(function(){
        playlistElement.innerText = name;
        playlistElement.style.opacity = "1";
        playlistElement.disabled = false;
    });
}