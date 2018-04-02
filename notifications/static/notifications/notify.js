var notify_badge_class;
var notify_menu_class;
var notify_api_url;
var notify_fetch_count;
var notify_unread_url;
var notify_mark_all_unread_url;
var notify_refresh_period = 15000;
var consecutive_misfires = 0;
var registered_functions = [];

function fill_notification_badge(data) {
    var badges = document.getElementsByClassName(notify_badge_class);
    if (badges) {
        for(var i = 0; i < badges.length; i++){
            badges[i].innerHTML = data.unread_count;
        }
    }
}

function formatDate(date) {
    var monthNames = [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ];
    var day = date.getDate();
    var monthIndex = date.getMonth();
    var year = date.getFullYear();
    var time = date.getHours();
    var minutes = date.getMinutes();
    return monthNames[monthIndex] + ' ' + day + ' at ' + time + ':' + minutes;
}

function fill_notification_list(data) {
    var menus = document.getElementsByClassName(notify_menu_class);
    console.log(notify_menu_class)
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            var message = "";
            if(typeof item.actor !== 'undefined'){
                message = item.actor;
            }
            if(typeof item.verb !== 'undefined'){
                message = message + " " + item.verb;
            }
            if(typeof item.target !== 'undefined'){
                message = message + " " + item.target;
            }
            if(typeof item.timestamp !== 'undefined'){
                notification_timestamp = formatDate(new Date(item.timestamp));
                // notification_timestamp = new Date(item.timestamp).toString();
            }
            if(item.verb === 'sent you a new message'){
                message = '<a class="dropdown-item notification_single" data-href="/inbox/notifications/mark-as-read/' + (item.id + 110909) + '/" href="/message/"><span class="notification_type_badge">Message</span><span class="notification_timestamp_badge">' + notification_timestamp + '</span><div class="notification_description_badge">' + message + '!</div></a>';
            }
            if(item.verb === 'sent you a pairing request'){
                message = '<a class="dropdown-item notification_single" data-href="/inbox/notifications/mark-as-read/' + (item.id + 110909) + '/" href="/profile/' + item.actor + '"><div class="notification_meta"><span class="notification_type_badge">Request</span><span class="notification_timestamp_badge">' + notification_timestamp + '</span></div><div class="notification_description_badge">' + message + '!</div></a>';
            }
            if(item.verb === 'accepted your request'){
                message = '<a class="dropdown-item notification_single" data-href="/inbox/notifications/mark-as-read/' + (item.id + 110909) + '/" href="/message/"><span class="notification_type_badge">New Pairing Partner!</span><span class="notification_timestamp_badge">' + notification_timestamp + '</span><div class="notification_description_badge">' + message + '! Begin chatting!</div></a>';
            }
            if(!item.unread){
                return '<li class="notification_list_item read_message">' + message + '</li>';
            } else {
                return '<li class="notification_list_item">' + message + '</li>';
            }
        }).join('')

        // Create and fill the Notification Inbox
        for (var i = 0; i < menus.length; i++){
            menus[i].innerHTML = '<div><p class="dropdown-header">Inbox</p></div>' +
            // '<div class="loading"><p>Please Wait...<p></div>' +
            messages + '<div><a class="dropdown-item" href="/inbox/notifications/" id="notification-all-hl">See all notifications</a></div>';
        }
        // Ajax mark as read upon notification check, then redirect
        $('#notification-all-hl').click(function(e){
            e.preventDefault();
            var this_ = $(this);
            var allNotifsUrl = this_.attr("href");
            if (allNotifsUrl){
                window.location = allNotifsUrl
            }
        });
        $(".notification_single").click(function(e){
            e.preventDefault()
            var this_ = $(this)
            var markAsReadUrl = this_.attr("data-href")
            if (markAsReadUrl){
               $.ajax({
                url: markAsReadUrl,
                method: "GET",
                data: {},
                success: function(data){
                    notificationNext = this_.attr("href");
                    window.location =  notificationNext;
                }, error: function(error){
                  console.log("uh oh")
                  // console.log(error)
                }
              })
        }})

    }
}

function register_notifier(func) {
    registered_functions.push(func);
}

function fetch_api_data() {
    var inbox = document.getElementsByClassName(notify_menu_class);

    // Loading Wheel
    // if (inbox) {
    //     console.log(inbox)
    //     for (var i = 0; i < inbox.length; i++){
    //         inbox[i].innerHTML = '<div class="loading"><p>Please Wait...<p></div>';
    //         $(".loading").show();
    //     }
    // }

    if (registered_functions.length > 0) {
        //only fetch data if a function is setup
        var r = new XMLHttpRequest();
        r.addEventListener('readystatechange', function(event){
            if (this.readyState === 4){
                if (this.status === 200){
                    consecutive_misfires = 0;
                    var data = JSON.parse(r.responseText);
                    registered_functions.forEach(function (func) { func(data); });
                }else{
                    consecutive_misfires++;
                }
            }
        })
        r.open("GET", notify_api_url+'?max='+notify_fetch_count, true);
        r.send();
    }
    if (consecutive_misfires < 10) {
        setTimeout(fetch_api_data,notify_refresh_period);
    } else {
        var badges = document.getElementsByClassName(notify_badge_class);
        if (badges) {
            for (var i = 0; i < badges.length; i++){
                badges[i].innerHTML = "!";
                badges[i].title = "Connection lost!"
            }
        }
    }
}

setTimeout(fetch_api_data, 1000);


// TODO: Base notifs symbol on seen/notseen, not count
// Remove New notif red dot
// Check if there are any unread
// if unread, red.
// $(document).ready(function(){
//     // TODO: .dropdown-toggle is too generic. for all dropdowns. change to more specific class
//     var $dropdownNotifications = $('.dropdown-toggle')
//     $dropdownNotifications.click(function(event){
//         console.log("test")
//         console.log($(".loading"))
//         $('.loading').show()
//         // event.preventDefault()
//         var $buttonData = $(this).serialize();
//         var $endpoint = $('.dropdown-notifications').attr('data-open-notifications')

//         $.ajax({
//             method: "POST",
//             url: $endpoint,
//             data: $buttonData,
//             success: handleSuccess,
//             error: handleError,
//         })
//     })

//     function handleSuccess(data, textStatus, jqXHR){
//         // No need to do anything here. Allow link click.
//         $('.loading').hide()
//         console.log("howdy success")
//         console.log(data)
//         console.log(textStatus)
//         console.log(jqXHR)

//         // window.location = buttonLocation

//     }

//     function handleError(jqXHR, textStatus, errorThrown){
//         console.log("howdy errors")
//         console.log(jqXHR)
//         console.log(textStatus)
//         console.log(errorThrown)

//     }
// // })


// $(document).ready(function(){

//     $(".notification_single").click(function(e){
//             // e.preventDefault()
//             console.log("IM WORKING")
//             var this_ = $(this)
//             var likeUrl = this_.attr("data-href")
//             var likeCount = parseInt(this_.attr("data-likes")) | 0
//             var addLike = likeCount + 1
//             var removeLike = likeCount - 1
//             if (likeUrl){
//                $.ajax({
//                 url: likeUrl,
//                 method: "GET",
//                 data: {},
//                 success: function(data){
//                   console.log(data)
//                   var newLikes;
//                   if (data.liked){
//                       updateText(this_, addLike, "Unlike")
//                   } else {
//                       updateText(this_, removeLike, "Like")
//                       // remove one like
//                   }
//                 }, error: function(error){
//                   console.log(error)
//                   console.log("error")
//                 }
//               })
//           }})
// })