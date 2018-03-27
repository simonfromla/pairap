$(function () {
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/loadhistory/";
    console.log("Connecting to " + ws_path);
    var loadhistorysocket = new ReconnectingWebSocket(ws_path);

    // Helpful debugging
    loadhistorysocket.onopen = function () {
        console.log("Connected to load-history chat socket");
    };
    loadhistorysocket.onclose = function () {
        console.log("Disconnected from load-history chat socket");
    };

    loadhistorysocket.onmessage = function (message) {
        // Decode the JSON
        console.log("Got websocket history message " + message.data);
        var data = JSON.parse(message.data);
        console.log("======")
        console.log(data)
        // Handle errors
        if (data.error) {
            alert(data.error);
            return;
        }
        var new_messages = data["messages"]

        var last_id = data["previous_id"]

        if(last_id == -1){
            $("#load_old_messages").remove();
            $("#last_message_id").text(last_id)
            if(new_messages.length == 0){
                return;
            }
        }
        else{
            $("#last_message_id").text(last_id)
        }

        var chat = $("#messages")

        for(var i=new_messages.length - 1; i>=0; i--){
            var ele = $('<li class="list-group-item"></li>')

            ele.append(
                '<span class="username">' + new_messages[i]['username'] +'</span>: '
            )

            ele.append(
                '<span class="username">' + new_messages[i]['message'] + '</span>'
            )

            chat.prepend(ele)
        }
    };

// `document` to target dynamically rendered content
    document.addEventListener('scroll', function (event) {
        if (event.target.id === 'messages') {
            if($("#messages").scrollTop() <= 50) {
                $("#load_old_messages").trigger('click');
            };
        };
    }, true /*Capture event*/);

    $(document).on("click", "#load_old_messages", function() {
        var message = {
            last_message_id: $('#last_message_id').text(),
            room: $("li.joined").attr("data-room-id")
        }
        loadhistorysocket.send(JSON.stringify(message));
        return false;
    })
});