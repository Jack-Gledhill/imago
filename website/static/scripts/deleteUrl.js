function deleteUrl(discrim) {
    $("#delete-error").removeClass("show");
    $("#delete-success").removeClass("show");

    $.ajax({
        url: `/api/delete/u/${discrim}`,
        type: "DELETE",
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            $("#delete-success").addClass("show");
            
            let element = document.getElementById(discrim);
            element.parentNode.removeChild(element);
        },
        error: function(res) {
            $("#delete-error").addClass("show");
        }
    });
};