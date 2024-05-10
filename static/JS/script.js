function redirect(path) {
    window.location.href = path;
}

function loadRecommandations() {
    fetch("/api/user/is_logged", {
        method: "GET",
      })
        .then((res) => res.text())
        .then((res) => {
          console.log(res);
          if(res === "session_invalid"){
            reco = document.getElementById("recommandations");
            reco.style.display = 'none';
          }
        });
}


function checkLogin() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    if (email !== "" && password !== "") {
      const data = new FormData();
      data.append("email", email);
      data.append("password", password);
  
      fetch("/api/user/login", {
        method: "POST",
        body: data,
      })
        .then((response) => response.text())
        .then((data) => {
          switch (data.trim()) {
            case "redirect_admin":
              window.location.href = "/index.php/admin-users";
              break;
            case "redirect_user":
              window.location.href = "/dashboard";
              break;
            case "bad_cred":
              alert("Bad credentials, please check your email and/or password");
              break;
          }
        });
    } else {
      alert("Please fill all fields");
    }
  }