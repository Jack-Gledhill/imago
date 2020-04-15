function delete_file(discrim) {
  swal({
      title: "Hold up!",
      text: "Are you sure you want to do this?",
      closeOnClickOutside: false,
      closeOnEsc: false,
      buttons: {
        no: {
            text: "Cancel",
            value: "no"
        },
        yes: {
            text: "Continue",
            value: "yes",
            closeModal: false
        },
    }
  }).then((option) => {
      switch (option) {
          case "no":
            swal.close();

            break;

          case "yes":
            $.ajax({
                url: `/api/delete/f/${discrim}`,
                type: "DELETE",
                headers: {
                    Authorization: getCookie("_auth_token")
                },
                success: function(res) {
                    swal.close();

                    let element = document.getElementById(discrim);
                    element.parentNode.removeChild(element);
                },
                error: function(res) {
                    swal.close();

                  swal({
                      title: "Unknown Error",
                      text: "Sorry, an unknown error occurred when trying to delete that file. Please try again.",
                      icon: "error"
                  });
                }
            });
      };
  });
};

function delete_url(discrim) {
  swal({
      title: "Hold up!",
      text: "Are you sure you want to do this?",
      closeOnClickOutside: false,
      closeOnEsc: false,
      buttons: {
        no: {
            text: "Cancel",
            value: "no"
        },
        yes: {
            text: "Continue",
            value: "yes",
            closeModal: false
        },
    }
  }).then((option) => {
      switch (option) {
          case "no":
            swal.close();

            break;

          case "yes":
            $.ajax({
                url: `/api/delete/u/${discrim}`,
                type: "DELETE",
                headers: {
                    Authorization: getCookie("_auth_token")
                },
                success: function(res) {
                    swal.close();

                    let element = document.getElementById(discrim);
                    element.parentNode.removeChild(element);
                },
                error: function(res) {
                    swal.close();

                  swal({
                      title: "Unknown Error",
                      text: "Sorry, an unknown error occurred when trying to delete that URL. Please try again.",
                      icon: "error"
                  });
                }
            });
      };
  });
};

function new_url() {
    let link_to = $("#link-box").val();
    let custom_name = $("#name-box").val();

    if (link_to.length === 0) {
        $("#link-header").html("<span style='color: #f04747;'>LINK TO -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#link-header").html("LINK TO");
    };

    if (link_to.length !== 0) {
        swal({
            title: "Hold up!",
            text: "Are you sure you want to do this?",
            closeOnClickOutside: false,
            closeOnEsc: false,
            buttons: {
                no: {
                    text: "Cancel",
                    value: "no"
                },
                yes: {
                    text: "Continue",
                    value: "yes",
                    closeModal: false
                },
            }
        }).then((option) => {
            switch (option) {
                case "no":
                    swal.close();

                    break;

                case "yes":
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
                            swal.close();

                            swal({
                                title: "URL Shortened",
                                text: "The URL has been successfully shortened.",
                                icon: "success",
                                timer: 5000
                            });

                            setTimeout(() => {
                                window.location.replace("/home/urls");
                            }, 5000)
                        },
                        error: function(res) {
                            swal.close();

                            if (res.status === 403) {
                                swal({
                                    title: "Improper URL",
                                    text: "Sorry, that URL is malformed. Please pick another.",
                                    icon: "error"
                                });
                            } if (res.status === 409) {
                                swal({
                                    title: "Already Shortened",
                                    text: "Sorry, that URL has already been shortened. Please pick another.",
                                    icon: "error"
                                });
                            } else {
                                swal({
                                    title: "Unknown Error",
                                    text: "Sorry, an error occurred. Please try again.",
                                    icon: "error"
                                });
                            };
                        }
                    });
            };
        });
    };
};

function reset_token(id) {
    if ($("#regen-button").hasClass("blocked")) return;

    swal({
        title: "Hold up!",
        text: "Are you sure you want to do this?",
        closeOnClickOutside: false,
        closeOnEsc: false,
        dangerMode: true,
        buttons: {
            no: {
                text: "Cancel",
                value: "no"
            },
            yes: {
                text: "Continue",
                value: "yes",
                closeModal: false
            },
        }
    }).then((option) => {
        switch (option) {
            case "no":
                swal.close();

                break;

            case "yes":
                $.ajax({
                    url: `/api/user/reset`,
                    type: "PUT",
                    contentType: "application/json",
                    data: JSON.stringify({
                        user_id: id
                    }),
                    headers: {
                        Authorization: getCookie("_auth_token")
                    },
                    success: function(res) {
                        swal.close();

                        $("#copy-button").attr("data-clipboard-text", res.new_token);

                        document.cookie = `_auth_token=${res.new_token}; path=/; expires=2038-01-19 04:14:07`;

                        $("#regen-button").removeClass("blue-button");
                        $("#regen-button").addClass("green-button");
                        
                        $("#regen-button").text("Renewed");

                        setTimeout(() => {
                            $("#regen-button").text("Renew");

                            $("#regen-button").addClass("blue-button");
                            $("#regen-button").removeClass("green-button");
                        }, 2000);
                    },
                    error: function(res) {
                        swal.close();

                        swal({
                            title: "Unknown Error",
                            text: "Sorry, an error occurred. Please try again.",
                            icon: "error"
                        });
                    }
                });
        };
    });
};

function edit_user(id) {
    if ($("#edit-button").hasClass("blocked")) return;

    swal({
        title: "Hold up!",
        text: "Are you sure you want to do this?",
        closeOnClickOutside: false,
        closeOnEsc: false,
        buttons: {
            no: {
                text: "Cancel",
                value: "no"
            },
            yes: {
                text: "Continue",
                value: "yes",
                closeModal: false
            },
        }
    }).then((option) => {
        switch (option) {
            case "no":
                swal.close();

                break;

            case "yes":
                let user_data = {
                    user_id: id,
                    new_values: {}
                };
                let nulls = ["", null, " ", undefined];

                let username = $("#username-box").val();
                let password = $("#password-box").val();
                let conf_password = $("#c-password-box").val();
                let display = $("#display-box").val();

                if (!nulls.includes(username)) {
                    user_data.new_values.username = username
                } if (!nulls.includes(password)) {
                    if (password !== conf_password) {
                        $("#password-header").html("<span style='color: #f04747;'>PASSWORD -</span> <span style='color: #f04747; font-weight: normal;'><i>Passwords do not match</i></span>");
                        
                        return $("#c-password-header").html("<span style='color: #f04747;'>CONFIRM PASSWORD -</span> <span style='color: #f04747; font-weight: normal;'><i>Passwords do not match</i></span>");
                    } else {
                        $("#password-header").html("PASSWORD");
                        $("#c-password-header").html("CONFIRM PASSWORD");
                    }

                    user_data.new_values.password = password
                } if (!nulls.includes(display)) {
                    user_data.new_values.display_name = display
                };

                $.ajax({
                    url: `/api/user/edit`,
                    type: "PUT",
                    contentType: "application/json",
                    data: JSON.stringify(user_data),
                    headers: {
                        Authorization: getCookie("_auth_token")
                    },
                    success: function(res) {
                        swal.close();

                        swal({
                            title: "User Edited",
                            text: "You have successfully edited yourself.",
                            icon: "success",
                            timer: 5000
                        });

                        $("#display-name").text(res.new_values.display_name)
                        document.cookie = `display_name=${res.new_values.display_name}; path=/; expires=2038-01-19 04:14:07`;
                    },
                    error: function(res) {
                        swal.close();

                        if (res.status === 409) {
                            swal({
                                title: "Username Unavailable",
                                text: "Sorry, that username is already registered. Please pick another.",
                                icon: "error"
                            });
                        } else {
                            swal({
                                title: "Unknown Error",
                                text: "Sorry, an error occurred. Please try again.",
                                icon: "error"
                            });
                        };
                    }
                });
        };
    });
};

function copy_token() {
    new ClipboardJS("[data-clipboard-copy]");

    $("#copy-button").removeClass("blue-button");
    $("#copy-button").addClass("green-button");
    
    $("#copy-button").text("Copied");

    setTimeout(() => {
        $("#copy-button").text("Copy");

        $("#copy-button").addClass("blue-button");
        $("#copy-button").removeClass("green-button");
    }, 2000);
}