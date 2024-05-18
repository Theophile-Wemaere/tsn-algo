function redirect(path) {
  window.location.href = path;
}

function logout() {
  window.location.href = "/api/user/logout";
}

function autoGrow(element) {
  element.style.height = "5px";
  element.style.height = (element.scrollHeight) + "px";
}

function loadRecommandations() {
  fetch("/api/user/is_logged", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      reco = document.getElementById("recommandations");
      if (res.code === "session_valid") {
        loadUserRecommandations();
      } else {
        reco.innerHTML = `
        <h2>Login on 𝕐 to see customs recommandations !</h2>
        <a href="/login" class="user-info">Login now</a>
        `;
      }
    });
}

function loadUserRecommandations() {
  fetch("/api/user/recommandations?t=user", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        reco = document.getElementById("users");
        res.data.forEach(function (user) {
          row = `
          <a href="/profile?id_user=${user.id}">
            <div class="user-row" id="recommandation-user-${user.id}">
              <img src="/static/pictures/${user.picture}.png">
              <div class="user-names">
                <b>${user.displayname}</b>
                <i>@${user.username}</i>
              </div>
              <div style="flex-grow:1"></div>
              <button onclick="event.preventDefault();followUser(${user.id})">Follow</button>
            </div>
          </a>
          `
          reco.innerHTML += row;
        });
      }
    });
}

function followUser(id_user) {
  fetch(`/api/user/relation?id_user=${id_user}&action=follow`, {
    method: "PATCH",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        userRow = document.getElementById(`recommandation-user-${id_user}`)
        if (userRow !== undefined) {
          userRow.remove();
        }
      } else {
        console.log(res);
      }
    });
}

function unfollowUser(id_user) {
  fetch(`/api/user/relation?id_user=${id_user}&action=unfollow`, {
    method: "PATCH",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        userRow = document.getElementById(`following-user-${id_user}`)
        hr = document.getElementById(`hr-${id_user}`)
        if (userRow !== undefined && hr !== undefined) {
          userRow.remove();
          hr.remove();
        }
      } else {
        console.log(res);
      }
    });
}

function loadUserMenu() {
  fetch("/api/user/is_logged", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "session_valid") {
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
        if (!window.location.pathname.startsWith("/post")) {
          button = document.getElementById("post-button")
          button.style.display = "flex"
        }
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
            window.location.href = "/home?onboarding=true";
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
  fetch(`/api/user/info/${id_user}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      const picture = document.getElementById("picture")
      const name = document.getElementById("name");
      const at = document.getElementById("at");
      const description = document.getElementById("description");
      const date = document.getElementById("date");
      const gender = document.getElementById("gender");
      const location = document.getElementById("location");
      const followers = document.getElementById("followers");
      const following = document.getElementById("following");

      document.title = `${res.displayname}'s profil`

      picture.src = `/static/pictures/${res.picture}.png`
      name.textContent = res.displayname;
      at.textContent = `@${res.username}`;
      description.textContent = res.description;
      date.innerHTML = `<i class="fa-solid fa-cake-candles"></i> Joined on ${res.creation}`;
      gender.innerHTML = `<i class="fa-solid fa-venus-mars"></i> ${res.gender}`;
      location.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${res.location}`;
      followers.innerHTML = `<a href="/followers?id_user=${id_user}"><b>${res.followers}</b> Followers</a>`
      following.innerHTML = `<a href="/following?id_user=${id_user}"><b>${res.following}</b> Following</a>`

      const tagsDiv = document.getElementById("preference-tags")
      tagsDiv.innerHTML = "";
      res.tags.forEach(tag => {
        tagsDiv.innerHTML += `
        <div class="row">
        <i class="fa-solid fa-hashtag"></i>
        ${tag}
        </div>
        `
      });

      if (res.is_logged === "yes" && window.location.pathname.startsWith("/profile")) {
        const buttons = document.querySelectorAll("#edit");
        buttons.forEach(button => {
          button.style.display = "block";
        });
        const button = document.getElementById("edit-preferences");
        button.setAttribute("self", "yes");
      } else {
        const button = document.getElementById("edit-preferences");
        button.setAttribute("self", "no");
      }
    });
}

function profileEditor() {
  fetch('/api/user/editor', {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      const onClickOutside = (e) => {
        if (e.target.className.includes("layer")) {
          removeEditor
            ();
          window.removeEventListener("click", onClickOutside);
        }
      };
      window.addEventListener("click", onClickOutside);
      fetch(`/api/user/info/0`, {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          const picture = document.getElementById("picture-edit")
          const name = document.getElementById("displayname-edit");
          const description = document.getElementById("description-edit");
          const location = document.getElementById("location-edit");

          picture.src = `/static/pictures/${res.picture}.png`
          name.value = res.displayname;
          description.textContent = res.description;
          location.value = res.location;
          switch (res.gender) {
            case "M":
              const M = document.getElementById("male");
              M.checked = true;
              break;
            case "F":
              const F = document.getElementById("female");
              F.checked = true;
              break;
            default:
              const X = document.getElementById("other");
              X.checked = true;
          }
        });
    });
}

function loadOnboarding() {
  fetch('/api/user/editor', {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      const title = document.getElementById("title-edit");
      title.textContent = "Welcome on 𝕐 !"
      const button = document.getElementById("exit-button");
      button.setAttribute('onclick', 'loadPreferencesEditor()')
      button.textContent = "Continue";
      fetch(`/api/user/info/0`, {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          const picture = document.getElementById("picture-edit")
          const name = document.getElementById("displayname-edit");
          const description = document.getElementById("description-edit");
          const location = document.getElementById("location-edit");

          picture.src = `/static/pictures/${res.picture}.png`
          name.value = res.displayname;
          description.textContent = res.description;
          location.value = res.location;
          switch (res.gender) {
            case "M":
              const M = document.getElementById("male");
              M.checked = true;
              break;
            case "F":
              const F = document.getElementById("female");
              F.checked = true;
              break;
            default:
              const X = document.getElementById("other");
              X.checked = true;
          }
        });
    });
}

function loadUserPreferenceEditor() {
  fetch('/api/user/tags?user=true', {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        const divTags = document.getElementById("selected-tags")
        divTags.innerHTML = "";
        for (var key in res.tags) {
          divTags.innerHTML += `
          <span class="subject-tag" id="tag-${res.tags[key]}">
          <i class="fa-solid fa-hashtag"></i>
          ${key}
          <div id="e"></div>
          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[key]})"></i>
        </span>`
        }
      }
    });
}

function loadPreferencesEditor() {
  removeEditor();
  fetch('/api/user/preferences', {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      if (window.location.pathname.startsWith("/profile")) {
        const onClickOutside = (e) => {
          if (e.target.className.includes("layer")) {
            removeEditor
              ();
            window.removeEventListener("click", onClickOutside);
          }
        };
        window.addEventListener("click", onClickOutside);
      }
      loadUserPreferenceEditor()
      fetch('/api/user/tags', {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          console.log(res)
          var tags = [];
          for (var key in res.tags) tags.push(key);
          if (res.code === "success") {
            $(function () {
              $("#subject-input").autocomplete({
                source: tags,
                select: function (event, ui) {
                  ui.item.value = ui.item.label;
                  $("#selected-tags").append(`
                        <span class="subject-tag" id="tag-${res.tags[ui.item.label]}">
                          <i class="fa-solid fa-hashtag"></i>
                          ${ui.item.label}
                          <div id="e"></div>
                          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[ui.item.label]})"></i>
                        </span>`);
                  $(this).val("");

                  return false;
                }
              });
            });
          }
        });
    });
}

function removeTag(id_tag) {
  var tag;
  if(id_tag.startsWith("tag-")) {
    tag = `${id_tag}`
  } else {
    tag = `tag-${id_tag}`
  }
  document.getElementById(tag).remove()
}

function selectTag() {
  fetch('/api/user/preferences', {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      const onClickOutside = (e) => {
        if (e.target.className.includes("layer")) {
          removeEditor
            ();
          window.removeEventListener("click", onClickOutside);
        }
      };
      window.addEventListener("click", onClickOutside);

      document.getElementById("title-edit").textContent = "Choose tags to identify your post"
      button = document.getElementById("exit-button")
      button.textContent = "Save tags"
      button.setAttribute("onclick","updateSelectedTags()")


      fetch('/api/user/tags', {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          console.log(res)
          var tags = [];
          for (var key in res.tags) tags.push(key);
          if (res.code === "success") {
            $(function () {
              $("#subject-input").autocomplete({
                source: tags,
                select: function (event, ui) {
                  ui.item.value = ui.item.label;
                  $("#selected-tags").append(`
                        <span class="subject-tag" id="tag-${res.tags[ui.item.label]}">
                          <i class="fa-solid fa-hashtag"></i>
                          ${ui.item.label}
                          <div id="e"></div>
                          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[ui.item.label]})"></i>
                        </span>`);
                  $(this).val("");

                  return false;
                }
              });
            });
          }
        });
    });
}

function updateSelectedTags() {
  const tagsDiv = document.getElementById("selected-tags");
  tagsRow = document.getElementById("tag-list")
  for (let i = 0; i < tagsDiv.children.length; i++) {
    tagsRow.innerHTML += `
    <div class="row" id="${tagsDiv.children[i].id}">
        <i class="fa-solid fa-hashtag"></i>
        ${tagsDiv.children[i].textContent}
        <i id="trash-remove" onclick="removeTag('${tagsDiv.children[i].id}')" class="fa-solid fa-trash"></i>
    </div>`
  }
  removeEditor();
}

function savePreferences() {
  const tagsDiv = document.getElementById("selected-tags");
  const tags = [];
  for (let i = 0; i < tagsDiv.children.length; i++) {
    tags.push(tagsDiv.children[i].id)
  }
  console.log(tags)
  const data = new FormData();
  data.append("tags", tags)
  fetch('/api/user/tags/update', {
    method: "PATCH",
    body: data
  })
    .then((res) => res.text())
    .then((res) => {
      console.log(res)
      if (res === "success") {
        removeEditor();
        loadUserProfile(0);
      }
    });
}

function removeEditor() {
  const layer = document.getElementById("layer");
  if (layer) {
    layer.remove();
  }
}

function updateProfile() {
  const name = document.getElementById("displayname-edit").value;
  const description = document.getElementById("description-edit").value;
  const location = document.getElementById("location-edit").value;
  const M = document.getElementById("male").checked;
  const F = document.getElementById("female").checked;
  var gender = "X";
  if (M) {
    gender = "M";
  } else if (F) {
    gender = "F";
  }
  const data = new FormData();
  data.append("displayname", name);
  data.append("description", description);
  data.append("location", location);
  data.append("gender", gender);
  fetch("/api/user/profile/update", {
    method: "PATCH",
    body: data,
  })
    .then((response) => response.text())
    .then((data) => {
      if (data.trim() === "success") {
        if (window.location.pathname.startsWith("/profile")) {
          removeEditor();
        }
        loadUserProfile(0);
      } else {
        windows.location.href = '/login';
      }
    });
}

function updatePicture() {
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/*";
  fileInput.onchange = function (event) {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      const data = new FormData();
      data.append("picture", selectedFile);

      fetch("/api/user/profile/picture", {
        method: "PATCH",
        body: data,
      })
        .then(response => response.json())
        .then(response => {
          if (response.code == "success") {
            console.log("Profile picture updated successfully!");
            picture = document.getElementById("picture-edit")
            picture.src = `/static/pictures/${response.hash}.png`
            loadUserMenu();
            loadUserProfile(0);
          } else {
            console.error("Error updating profile picture:", response.code);
            alert("Error updating profile picture:" + response.code)
          }
        })
        .catch(error => {
          console.error("Error sending file:", error);
        });
    }
  };
  fileInput.click();
}

function loadUserFollowers(id_user) {
  fetch(`/api/user/followers/${id_user}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      if (res.code === "success") {
        let row1 = document.getElementById("row1");
        row1.setAttribute("onClick", `redirect("/profile?id_user=${id_user}")`)
        var css = `
        .row#row1:hover {
          background-color: #FFFFFF;
          cursor:pointer;
          color: black;
        }`
        var style = document.createElement('style')
        if (style.styleSheet) {
          style.styleSheet.cssText = css;
        } else {
          style.appendChild(document.createTextNode(css));
        }
        document.getElementsByTagName('head')[0].appendChild(style);
        let row2 = document.getElementById("row2");
        row2.setAttribute("class", "cell")
        row2.innerHTML = `
        <div class="row">
        <a href="/followers?id_user=${id_user}"><div class="row current-tab"><h2>Followers</h2></div></a>
        <a href="/following?id_user=${id_user}"><div class="row other-tab"><h2>Following</h2></div></a>
        </div>`;
        row2.innerHTML += `<div class="cell" id="follows"></div>`
        follows = document.getElementById("follows")
        res.data.forEach(function (user) {
          row = `
          <a href="/profile?id_user=${user.id}">
            <div class="user-row" id="follower-user-${user.id}">
              <img src="/static/pictures/${user.picture}.png">
              <div class="user-names">
                <b>${user.displayname}</b>
                <i>@${user.username}</i>
                <div class="row" id="description">
                ${user.description}
                </div>
              </div>
              <div style="flex-grow:1"></div>
            </div>
          </a>
          <hr id="hr-${user.id}">
          `
          follows.innerHTML += row;
        });
      }
    });
}

function loadUserFollowing(id_user) {
  fetch(`/api/user/following/${id_user}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      if (res.code === "success") {
        let row1 = document.getElementById("row1");
        row1.setAttribute("onClick", `redirect("/profile?id_user=${id_user}")`)
        var css = `
        .row#row1:hover {
          background-color: #FFFFFF;
          cursor:pointer;
          color: black;
        }`
        var style = document.createElement('style')
        if (style.styleSheet) {
          style.styleSheet.cssText = css;
        } else {
          style.appendChild(document.createTextNode(css));
        }
        document.getElementsByTagName('head')[0].appendChild(style);
        let row2 = document.getElementById("row2");
        row2.setAttribute("class", "cell")
        row2.innerHTML = `
        <div class="row">
        <a href="/followers?id_user=${id_user}"><div class="row other-tab"><h2>Followers</h2></div></a>
        <a href="/following?id_user=${id_user}"><div class="row current-tab"><h2>Following</h2></div></a>
        </div>`;
        row2.innerHTML += `<div class="cell" id="follows"></div>`
        follows = document.getElementById("follows")
        res.data.forEach(function (user) {
          row = `
          <a href="/profile?id_user=${user.id}">
            <div class="user-row" id="following-user-${user.id}">
              <img src="/static/pictures/${user.picture}.png">
              <div class="user-names">
                <b>${user.displayname}</b>
                <i>@${user.username}</i>
                <div class="row" id="description">
                ${user.description}
                </div>
              </div>
              <div style="flex-grow:1"></div>`;
          if (res.is_logged == "yes") {
            row += `<button onclick="event.preventDefault();unfollowUser(${user.id})">Unfollow</button>`;
          }
          row += `
            </div>
          </a>
          <hr id="hr-${user.id}">
          `;
          follows.innerHTML += row;
        });
      }
    });
}