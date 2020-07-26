function login() {
    let username = $("#username").val();
    let password = $("#password").val();

    $("#incorrect").removeClass("show");
    $("#missing").removeClass("show");

    if (username.length === 0) {
        return $("#missing").addClass("show");
    } if (password.length === 0) {
        return $("#missing").addClass("show");
    }

    $.ajax({
        url: "/api/authenticate",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            username: username,
            password: password
        }),
        success: function(res) {
            document.cookie = `_auth_token=${res.token}; path=/; expires=2038-01-19 04:14:07`;
            window.location.replace("/home");
        },
        error: function(res) {
            $("#incorrect").addClass("show");
        }
    });
};

$(document).ready(function () {
    var time = new Date();

    if (time.getHours() >= 18) {
        $("body").css({backgroundImage: "url(https://teknetcontent.com/img/discord_dark.png)"});
    } else {
        $("body").css({backgroundImage: "url(https://teknetcontent.com/img/discord_light.jpg)"});
    };
});