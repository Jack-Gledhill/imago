function toggleAdmin(id) {
    $("#toggle-success").removeClass("show");
    $("#toggle-success").removeClass("show");

    $.ajax({
        url: `/api/user/edit`,
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify({
            id: id,
            new_values: {
                admin: "toggle"
            }
        }),
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            let element = document.getElementById(`${id}`);
            let admin_value = "???"

            if (res.new_values.admin) {
                admin_value = '<i class="fas fa-check"></i>';
            } else {
                admin_value = '<i class="fas fa-times"></i>';
            };

            element.children[2].innerHTML = admin_value;
        
            $("#toggle-success").addClass("show");
        },
        error: function(res) {
            $("#toggle-error").addClass("show");
        }
    });
};