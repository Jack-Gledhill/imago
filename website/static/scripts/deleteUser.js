function deleteUser(id) {
    $("#delete-error").removeClass("show");
    $("#delete-success").removeClass("show");

    $.ajax({
        url: `/api/user/delete`,
        type: "DELETE",
        contentType: "application/json",
        data: JSON.stringify({
            id: id
        }),
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            let element = document.getElementById(id);
            element.parentNode.removeChild(element);
    
            $("#delete-success").addClass("show");
        },
        error: function(res) {
            $("#delete-error").addClass("show");
        }
    });
};