function uploadFile(file) {
    let form_data = new FormData();
    form_data.append("upload", file);

    $("#upload-error").removeClass("show");

    $.ajax({
        url: `/api/upload`,
        type: "POST",
        headers: {
            Authorization: getCookie("_auth_token")
        },
        data: form_data,
        contentType: false,
        processData: false,
        success: function(res) {
            window.location.reload(false);
        },
        error: function(res) {
            $("#upload-error").addClass("show");
        }
    });
};