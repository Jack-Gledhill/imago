function editUser(id, has_confirm = true) {
    $("#save").addClass("is-loading");

    let user_data = {
        id: id,
        new_values: {}
    };
    let nulls = ["", null, " ", undefined];

    let username = $("#username").val();
    let password = $("#password").val();

    if (has_confirm) {
        let conf_password = $("#confirm").val();
        $("#edit-incorrect").removeClass("show");
    }

    $("#edit-missing").removeClass("show");
    $("#edit-taken").removeClass("show");
    $("#edit-error").removeClass("show");
    $("#edit-success").removeClass("show");

    if (!nulls.includes(username)) {
        user_data.new_values.username = username
    } if (!nulls.includes(password)) {
        if (has_confirm) {
            if (password !== conf_password) {
                $("#save").removeClass("is-loading");
                return $("#edit-incorrect").addClass("show");
            }
        }

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
            $("#edit-success").addClass("show");
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