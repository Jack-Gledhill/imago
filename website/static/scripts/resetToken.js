function resetToken(id) {
    $("#regen").addClass("is-loading");
    
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
            $("#token-proxy").html(res.new_token);

            $("#regen").addClass("is-success");
            $("#regen").removeClass("is-info");
            $("#regen").html(`<span class="icon is-small">
                <i class="fas fa-check"></i>
            </span>
            <span>Regenerated</span>`);

            $("#regen").attr("disabled", true);

            document.cookie = `_auth_token=${res.new_token}; path=/; expires=2038-01-19 04:14:07`;
        },
        error: function(res) {
            $("#regen-error").addClass("show");
        }
    });

    $("#regen").removeClass("is-loading");
};