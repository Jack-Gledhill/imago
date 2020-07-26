function newUser() {
    $("#new").addClass("is-loading");

    let username = $("#username").val();
    let password = $("#password").val();
    let admin = $("#admin").prop("checked");

    $("#new-taken").removeClass("show");
    $("#new-missing").removeClass("show");
    $("#new-error").removeClass("show");

    if (username.length === 0 || password.length === 0) {
        $("#new").removeClass("is-loading");
        return $("#new-missing").addClass("show");
    }

    if (admin === undefined) {
        admin = false;
    }
     
    $.ajax({
        url: `/api/user/new`,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            username: username,
            password: password,
            admin: admin
        }),
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            window.location.replace("/admin");
        },
        error: function(res) {
            if (res.status === 409) {
                $("#new-taken").addClass("show");
            } else {
                $("#new-error").addClass("show");
            };
        }
    });

    $("#new").removeClass("is-loading");
};