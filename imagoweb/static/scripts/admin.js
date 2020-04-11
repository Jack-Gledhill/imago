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
                  url: `/api/delete/${discrim}`,
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

function restore_file(discrim) {
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
                  url: `/api/restore/${discrim}`,
                  type: "POST",
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
                        text: "Sorry, an unknown error occurred when trying to restore that file. Please try again.",
                        icon: "error"
                    });
                  }
              });
        };
    });
};

function toggle_admin(id) {
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
                    url: `/api/user/edit`,
                    type: "PUT",
                    contentType: "application/json",
                    data: JSON.stringify({
                        user_id: id,
                        new_values: {
                            admin: "toggle"
                        }
                    }),
                    headers: {
                        Authorization: getCookie("_auth_token")
                    },
                    success: function(res) {
                        swal.close();

                        let element = document.getElementById(`${id}`);
                        let admin_value = "???"

                        if (res.new_values.admin) {
                            admin_value = "Yes";
                        } else {
                            admin_value = "No";
                        };

                        element.children[3].innerText = admin_value;

                        swal({
                            title: "Toggled",
                            text: "Administrator status has been toggled.",
                            icon: "success",
                            timer: 5000
                        });
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

function reset_token(id) {
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
                        swal({
                            title: "Token Reset",
                            text: "This user's API token has been reset.",
                            icon: "success",
                            timer: 5000
                        });
                    },
                    error: function(res) {
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

function delete_user(id) {
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
                    url: `/api/user/delete`,
                    type: "DELETE",
                    contentType: "application/json",
                    data: JSON.stringify({
                        user_id: id
                    }),
                    headers: {
                        Authorization: getCookie("_auth_token")
                    },
                    success: function(res) {
                        let element = document.getElementById(id);
                        element.parentNode.removeChild(element);
                
                        swal({
                            title: "User Deleted",
                            text: "The user was successfully deleted.",
                            icon: "success",
                            timer: 5000
                        });
                    },
                    error: function(res) {
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
                let display = $("#display-box").val();

                if (!nulls.includes(username)) {
                    user_data.new_values.username = username
                } if (!nulls.includes(password)) {
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
                            text: "The user has been successfully edited.",
                            icon: "success",
                            timer: 5000
                        });

                        setTimeout(() => {
                            window.location.replace("/home/admin");
                        }, 5000)
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
                            console.log(res);

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

function new_user() {
    let username = $("#username-box").val();
    let password = $("#password-box").val();
    let display = $("#display-box").val();
    let admin = $("#admin-box").prop("checked");

    if (username.length === 0) {
        $("#username-header").html("<span style='color: #f04747;'>USERNAME -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#username-header").html("USERNAME");
    };

    if (password.length === 0) {
        $("#password-header").html("<span style='color: #f04747;'>PASSWORD -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#password-header").html("PASSWORD");
    };

    if (display.length === 0) {
        $("#display-header").html("<span style='color: #f04747;'>DISPLAY NAME -</span> <span style='color: #f04747; font-weight: normal;'><i>This field is required</i></span>");
    } else {
        $("#display-header").html("DISPLAY NAME");
    };

    if (username.length !== 0 & password.length !== 0 & display.length !== 0) {
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
                        url: `/api/user/new`,
                        type: "POST",
                        contentType: "application/json",
                        data: JSON.stringify({
                            username: username,
                            password: password,
                            display_name: display,
                            admin: admin
                        }),
                        headers: {
                            Authorization: getCookie("_auth_token")
                        },
                        success: function(res) {
                            swal.close();

                            swal({
                                title: "User Created",
                                text: "The user has been successfully created.",
                                icon: "success",
                                timer: 5000
                            });

                            setTimeout(() => {
                                window.location.replace("/home/admin");
                            }, 5000)
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
};