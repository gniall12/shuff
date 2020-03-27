function shuffle(id, name) {
    var playlistDiv = document.getElementById(id + "div");
    var playlistElement = document.getElementById(id);
    playlistElement.innerText = "Loading...";
    playlistElement.style.opacity = "0.5";
    playlistElement.disabled = true;
    $.get("/shuffle", {
        "id": id,
        "name": name
    }, function(data) {
        var newPlaylistDiv = document.createElement("div");
        newPlaylistDiv.setAttribute("class", "col-md-4");
        newPlaylistDiv.setAttribute("id", data["id"] + "div");

        var newPlaylistButton = document.createElement("button");
        newPlaylistButton.setAttribute("class", "button shuff-btn playlist");
        newPlaylistButton.setAttribute("id", data["id"]);
        newPlaylistButton.setAttribute("onclick", "shuffle('" + data["id"] + "', '" + data["name"] + "')");
        newPlaylistButton.innerText = data["name"];
        
        newPlaylistDiv.appendChild(newPlaylistButton);
        playlistDiv.parentNode.insertBefore(newPlaylistDiv, playlistDiv.nextSibling);
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