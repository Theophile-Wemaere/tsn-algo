function redirect(path) {
    window.location.href = path;
}

function logout() {
  window.location.href = "/api/user/logout";
}

function loadRecommandations() {
  fetch("/api/user/is_logged", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      console.log(res);
      if(res.code === "session_valid"){
        reco = document.getElementById("recommandations");
        reco.style.display = 'block';
      }
    });
}

function loadUserMenu() {
    fetch("/api/user/is_logged", {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          if(res.code === "session_valid") {
            // set username and profile picture
            reco = document.getElementById("user-info");
            imageUrl = `/static/pictures/${res.picture}.png`
            content = `@${res.username} <img src="${imageUrl}" alt="${res.username}'s profile picture">`
            reco.innerHTML = content;
            reco.style.paddingLeft = "10px";

            // set redirect to profile
            link = document.getElementById("login-link")
            link.href = "/profile"

            // display logout button
            hr = document.getElementById("hr-logout")
            hr.style.display = "block";
            row = document.getElementById("row-logout")
            row.style.display = "flex"

            // display post buttons
            button = document.getElementById("post-button")
            button.style.display = "flex"
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
              window.location.href = "/home";
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

function passwordCheck() {
  const error = document.getElementById("error-password")
  const password = document.getElementById("password").value;
  const cpassword = document.getElementById("cpassword").value;
  const button = document.getElementById("btn-user")

  if (password !== cpassword) {
    error.style.display = "block";
    button.disabled = true;
    button.style.pointerEvents = "none";
    button.style.opacity = "0.5";
  } else {
    error.style.display = "none";
    button.disabled = false;
    button.style.pointerEvents = "auto";
    button.style.opacity = "1";
  }
}

function signIn() {
  const email = document.getElementById("email").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const cpassword = document.getElementById("cpassword").value;

  if (password !== cpassword) {
    alert("Please make sure the passwords matchs")
    return;
  }

  if (email !== "" && username !== "" && cpassword !== "") {
    const data = new FormData();
    data.append("email", email);
    data.append("username", username);
    data.append("password", cpassword);
    fetch("/api/user/signin", {
      method: "POST",
      body: data,
    })
      .then((response) => response.text())
      .then((data) => {
        switch (data.trim()) {
          case "redirect_user":
            window.location.href = "/home";
            break;
          case "bad_email":
            alert("Error, this email is already used, please use another one");
            break;
          case "bad_username":
            alert("Error, this username is already used, please find another one");
            break;
        }
      });
  } else {
    alert("Please fill all fileds");
  }
}

function loadUserProfile(id_user) {
  console.log(`going to load id ${id_user}`)
  fetch(`/api/user/info/${id_user}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      console.log(res);
      const name = document.getElementById("name");
      const at = document.getElementById("at");
      const description = document.getElementById("description");
      const date = document.getElementById("date");
      const gender = document.getElementById("gender");
      const location = document.getElementById("location");
      const followers = document.getElementById("followers");
      const following = document.getElementById("following");

      name.textContent = res.displayname;
      at.textContent = `@${res.username}`;
      description.textContent = res.description;
      date.innerHTML = `<i class="fa-solid fa-cake-candles"></i> Joined on ${res.creation}`;
      gender.innerHTML = `<i class="fa-solid fa-venus-mars"></i> ${res.gender}`;
      location.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${res.localisation}`;
      followers.innerHTML = `<b>${res.followers}</b> Followers`
      following.innerHTML = `<b>${res.following}</b> Following`
    });
}