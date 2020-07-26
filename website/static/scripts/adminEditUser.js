function editUser(id) {
    $("#save").addClass("is-loading");

    let user_data = {
        id: id,
        new_values: {}
    };
    let nulls = ["", null, " ", undefined];

    let username = $("#username").val();
    let password = $("#password").val();

    $("#edit-missing").removeClass("show");
    $("#edit-taken").removeClass("show");
    $("#edit-error").removeClass("show");
    $("#edit-success").removeClass("show");

    if (!nulls.includes(username)) {
        user_data.new_values.username = username
    } if (!nulls.includes(password)) {
        user_data.new_values.password = password
    }

    $.ajax({
        url: `/api/user/edit`,
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify(user_data),
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            window.location.replace("/admin");
        },
        error: function(res) {
            if (res.status === 409) {
                $("#edit-taken").addClass("show"); 
            } else {
                $("#edit-error").addClass("show");
            };
        }
    });

    $("#save").removeClass("is-loading");
};