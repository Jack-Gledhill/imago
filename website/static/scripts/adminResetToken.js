function resetToken(id) {
    $("#regen-error").removeClass("show");
    $("#regen-success").removeClass("show");

    $.ajax({
        url: `/api/user/reset`,
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify({
            id: id
        }),
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            $("#regen-success").addClass("show");
        },
        error: function(res) {
            $("#regen-error").addClass("show");
        }
    });
};