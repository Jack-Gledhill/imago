$(document).ready(function() {
    // =========================
    // Print version information
    // =========================
    let version = $("#version-proxy").data("version-info");
    console.log(`%c[Release Info]%c Release: ${version['release']}, Version: ${version['number']}, Build: ${version['hash']}`, "color: purple", "color: default");

    // ========================
    // Detect dev tools opening
    // ========================
    window.addEventListener("devtoolschange", event => {
      if (event.detail.isOpen) {
              // ========================================
              // Warn user about the dangers of dev tools
              // ========================================
              console.log("%cSlow down!", "color: #7289DA; font-size: 75px; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;")
              console.log("%cPasting anything here may result in attackers gaining access to your account.", "color: red; font-size: 25px;")
              console.log("%cIf someone told you to paste something here, there's a high chance it's a scam. Unless you know what you're doing, close this window and stay safe.", "font-size: 15px;")
          };
    });
});

// Courtesy of w3schools
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}