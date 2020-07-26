function newUrl() {
    $("#shorten").addClass("is-loading");

    let link_to = $("#link").val();
    let custom_name = $("#name").val();

    $("#new-missing").removeClass("show");
    $("#new-incorrect").removeClass("show");
    $("#new-taken").removeClass("show");
    $("#new-error").removeClass("show");

    if (link_to.length === 0) {
        $("#shorten").removeClass("is-loading");
        return $("#new-missing").addClass("show");
    };

    $.ajax({
        url: `/api/shorten`,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            url: link_to
        }),
        headers: {
            Authorization: getCookie("_auth_token"),
            "URL-Name": custom_name
        },
        success: function(res) {
            window.location.replace("/home/urls");
        },
        error: function(res) {
            if (res.status === 403) {
               $("#new-incorrect").addClass("show"); 
            } if (res.status === 409) {
                $("#new-taken").addClass("show");
            } else {
                $("#new-error").addClass("show");
            };
        }
    });

    $("#shorten").removeClass("is-loading");
};