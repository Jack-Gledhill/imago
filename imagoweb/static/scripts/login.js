function login() {
    let username = $("#username-box").val();
    let password = $("#password-box").val();

    $(".red-banner").removeClass("show");

    if (username.length === 0) {
        $("#username-header").html("<span style='color: #f04747;'>USERNAME -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#username-header").html("USERNAME");
    };

    if (password.length === 0) {
        $("#password-header").html("<span style='color: #f04747;'>PASSWORD -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#password-header").html("PASSWORD");
    };

    if (username.length !== 0 & password.length !== 0) {
        $.ajax({
            url: "/api/authenticate",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                username: username,
                password: password
            }),
            success: function(res) {
                document.cookie = `_auth_token=${res.api_token}; path=/; expires=2038-01-19 04:14:07`;
                document.cookie = `display_name=${res.display_name}; path=/; expires=2038-01-19 04:14:07`;
                window.location.replace("/home");
            },
            error: function(res) {
                $(".red-banner").addClass("show");
            }
        });
    }
};