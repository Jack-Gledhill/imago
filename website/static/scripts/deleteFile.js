function deleteFile(discrim) {
    $("#delete-error").removeClass("show");
    $("#delete-success").removeClass("show");
    
    $.ajax({
        url: `/api/delete/f/${discrim}`,
        type: "DELETE",
        headers: {
            Authorization: getCookie("_auth_token")
        },
        success: function(res) {
            let element = document.getElementById(discrim);
            element.parentNode.removeChild(element);

            $("#delete-success").addClass("show");
        },
        error: function(res) {
            $("#delete-error").addClass("show");
        }
    });
};