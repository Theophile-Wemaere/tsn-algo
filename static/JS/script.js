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

