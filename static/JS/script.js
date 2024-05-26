function redirect(path) {
  window.location.href = path;
}

function logout() {
  window.location.href = "/api/user/logout";
}

function autoGrow(element) {
  element.style.height = "5px";
  element.style.height = element.scrollHeight + "px";
}

function searchBar(event) {
  if (event.key == "Enter") {
    inputBar = document.getElementById("search-input");
    search = inputBar.value;
    inputBar.value = "";
    range = document.getElementById("search-range").value;
    redirect(`/search?range=${range}&q=${search}`);
  }
}

function highlightWord(text, word) {
  return text.replace(
    word,
    `
  <b style="color:black;background-color:yellow;">${word}</b>`
  );
}

function searchQuery(range, query) {
  document.getElementById("search-input").value = query;
  document.getElementById("search-range").value = range;
  url = "";
  if (range === "posts") {
    url = `/api/post/search?q=${query}`;
  } else if (range === "users") {
    url = `/api/user/search?q=${query}`;
  }
  fetch(url, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        container = document.getElementById("search-container");
        if (res.data.length > 0) {
          console.log(res.data);
          res.data.forEach((data) => {
            row = "";
            if (range === "posts") {
              row = `
              <a href="/post/view/${data.id_post}">
                <div class="post-block">
                    <h2 id="post-title">${data.title}</h2>
                    <div id="post-author" onclick="event.preventDefault();redirect('/profile?id_user=${data.id_author}')">
                        <img src="/static/pictures/${data.author_picture}.png">
                        <h3>${data.author}, on ${data.created_at}</h3>
                    </div>
                    <div class="post-content ql-editor">
                    ${data.content}
                    </div>
                </div>
              </a>`;
            } else if (range === "users") {
              desc = data.description === null ? "" : data.description;
              row = `
              <a class="a-user" href="/profile?id_user=${data.id}">
                <div class="user-row" id="following-user-${data.id}">
                  <img src="/static/pictures/${data.picture}.png">
                  <div class="user-names">
                    <b>${highlightWord(data.displayname, query)}</b>
                    <i>@${highlightWord(data.username, query)}</i>
                    <div class="row" id="description">
                    ${highlightWord(desc, query)}
                    </div>
                  </div>
                  <div style="flex-grow:1"></div>
                </div>
              </a>`;
            }

            container.innerHTML += row;
          });
        } else {
          alert("No results found :(");
        }
      } else {
        console.log(res);
      }
    });
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
        loadPostRecommandations();
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
          `;
          reco.innerHTML += row;
        });
      }
    });
}

function loadPostRecommandations() {
  fetch("/api/user/recommandations?t=post", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        reco = document.getElementById("posts");
        res.posts.forEach(function (post) {
          row = `
          <a href="/post/view/${post.id_post}">
              <b>${post.title}</b>
              <i>By ${post.author},</br>on ${post.created_at}</i>
              <div id="post-reco-content">${post.content}</div>
              <div class="row">
              <i class="fa-solid fa-thumbs-up"></i>${post.like}
              </div>
            </div>
          </a>
          `;
          reco.innerHTML += row;
        });
      }
    });
}

function followUser(id_user, from = undefined) {
  fetch(`/api/user/relation?id_user=${id_user}&action=follow`, {
    method: "PATCH",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        if (from !== undefined) {
          loadUserProfile(from);
        } else {
          userRow = document.getElementById(`recommandation-user-${id_user}`);
          if (userRow !== undefined) {
            userRow.remove();
          }
        }
      } else {
        console.log(res);
      }
    });
}

function unfollowUser(id_user, from = undefined) {
  fetch(`/api/user/relation?id_user=${id_user}&action=unfollow`, {
    method: "PATCH",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        if (from !== undefined) {
          loadUserProfile(from);
        } else {
          userRow = document.getElementById(`following-user-${id_user}`);
          hr = document.getElementById(`hr-${id_user}`);
          if (userRow !== undefined && hr !== undefined) {
            userRow.remove();
            hr.remove();
          }
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
        imageUrl = `/static/pictures/${res.picture}.png`;
        content = `@${res.username} <img src="${imageUrl}" alt="${res.username}'s profile picture">`;
        reco.innerHTML = content;
        reco.style.paddingLeft = "10px";

        // set redirect to profile
        link = document.getElementById("login-link");
        link.href = "/profile";

        // display logout button
        hr = document.getElementById("hr-logout");
        hr.style.display = "block";
        row = document.getElementById("row-logout");
        row.style.display = "flex";

        // display post buttons
        if (
          !window.location.pathname.startsWith("/post/create") &&
          !window.location.pathname.startsWith("/post/edit")
        ) {
          button = document.getElementById("post-button");
          button.style.display = "flex";
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
  const error = document.getElementById("error-password");
  const password = document.getElementById("password").value;
  const cpassword = document.getElementById("cpassword").value;
  const button = document.getElementById("btn-user");

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
    alert("Please make sure the passwords matchs");
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
            alert(
              "Error, this username is already used, please find another one"
            );
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
      console.log(res);
      const picture = document.getElementById("picture");
      const name = document.getElementById("name");
      const at = document.getElementById("at");
      const description = document.getElementById("description");
      const date = document.getElementById("date");
      const gender = document.getElementById("gender");
      const location = document.getElementById("location");
      const followers = document.getElementById("followers");
      const following = document.getElementById("following");

      document.title = `${res.displayname}'s profil`;

      picture.src = `/static/pictures/${res.picture}.png`;
      name.textContent = res.displayname;
      at.textContent = `@${res.username}`;
      description.innerHTML = res.description;
      date.innerHTML = `<i class="fa-solid fa-cake-candles"></i> Joined on ${res.creation}`;
      gender.innerHTML = `<i class="fa-solid fa-venus-mars"></i> ${res.gender}`;
      location.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${res.location}`;
      followers.innerHTML = `<a href="/followers?id_user=${id_user}"><b>${res.followers}</b> Followers</a>`;
      following.innerHTML = `<a href="/following?id_user=${id_user}"><b>${res.following}</b> Following</a>`;

      const tagsDiv = document.getElementById("preference-tags");
      tagsDiv.innerHTML = "";

      res.tags.forEach((tag) => {
        tagsDiv.innerHTML += `
        <div class="row">
        <i class="fa-solid fa-hashtag"></i>
        ${tag}
        </div>
        `;
      });

      if (
        res.is_logged === "yes" &&
        window.location.pathname.startsWith("/profile")
      ) {
        const buttons = document.querySelectorAll("#edit");
        buttons.forEach((button) => {
          button.style.display = "block";
        });
        const button = document.getElementById("edit-preferences");
        button.setAttribute("self", "yes");
      } else {
        const button = document.getElementById("edit-preferences");
        button.setAttribute("self", "no");
      }

      if (res.is_logged !== "yes" && res.session_ok === "yes") {
        // display "send messages" button
        buttonMessage = document.getElementById("send-message");
        buttonMessage.style.display = "block";
        buttonMessage.setAttribute(
          "onclick",
          `redirect('/messages?conv=${id_user}')`
        );

        buttonFollow = document.getElementById("follow-profile-button");
        if (!res.is_followed) {
          buttonFollow.style.display = "block";
          buttonFollow.setAttribute(
            "onclick",
            `followUser('${id_user}','${id_user}')`
          );
        } else if (res.is_followed) {
          buttonFollow.innerHTML = 'UnFollow <i class="fa-solid fa-xmark"></i>';
          buttonFollow.style.display = "block";
          buttonFollow.classList.add("unfollow-button");
          buttonFollow.setAttribute(
            "onclick",
            `unfollowUser('${id_user}','${id_user}')`
          );
        }

        if (res.is_follower && res.is_followed) {
          console.log("dual");
          name.innerHTML += "<p>You follow each other</p>";
        } else if (res.is_follower && !res.is_followed) {
          console.log("incoming");
          name.innerHTML += "<p>Follows you</p>";
        } else if (!res.is_follower && res.is_followed) {
          console.log("outcoming");
          name.innerHTML += "<p>Following</p>";
        }
      }
    });
}

function loadUserActivity(id_user, activity = "posts") {
  fetch(`/api/user/activity/${id_user}?type=${activity}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        document.querySelectorAll(".focused").forEach((div) => {
          div.classList.remove("focused");
        });
        tab = document.getElementById(`tab-${activity}`);
        tab.classList.add("focused");

        if (res.is_logged !== "yes") {
          dislikes = document.getElementById("tab-dislikes");
          if (dislikes) {
            dislikes.remove();
          }
          saved = document.getElementById("tab-saved");
          if (saved) {
            saved.remove();
          }
        }

        container = document.getElementById(`container`);

        container.innerHTML = "";
        if (res.posts.length > 0) {
          res.posts.forEach(function (post) {
            row = `
            <a href="/post/view/${post.id_post}">
                <div class="post-block">
                    <h2 id="post-title">${post.title}</h2>
                    <div id="post-author" onclick="event.preventDefault();redirect('/profile?id_user=${post.id_author
              }')">
                        <img src="/static/pictures/${post.author_picture}.png">
                        <h3>${post.author}, on ${post.created_at}</h3>
                    </div>
                    <div class="post-content ql-editor">
                    ${post.content}
                    </div>
                  <div id="stats">
                    ${getStatsBar(post)}
                  </div>
                </div>
            </a>
            `;
            container.innerHTML += row;
          });
        } else {
          container.innerHTML += `<h1>No activity for this category</h1>`;
        }
      } else {
        console.log(res);
      }
    });
}

function loadSettings() {
  fetch("/api/user/settings", {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "login") {
        redirect("/login");
      } else {
        document.body.innerHTML += res;
        const onClickOutside = (e) => {
          if (e.target.className.includes("layer")) {
            removeEditor();
            window.removeEventListener("click", onClickOutside);
          }
        };
        window.addEventListener("click", onClickOutside);
      }
    });
}

function profileEditor() {
  fetch("/api/user/editor", {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "login") {
        redirect("/login");
      } else {
        document.body.innerHTML += res;
        const onClickOutside = (e) => {
          if (e.target.className.includes("layer")) {
            removeEditor();
            window.removeEventListener("click", onClickOutside);
          }
        };
        window.addEventListener("click", onClickOutside);
        fetch(`/api/user/info/0`, {
          method: "GET",
        })
          .then((res) => res.json())
          .then((res) => {
            const picture = document.getElementById("picture-edit");
            const name = document.getElementById("displayname-edit");
            const description = document.getElementById("description-edit");
            const location = document.getElementById("location-edit");

            picture.src = `/static/pictures/${res.picture}.png`;
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
      }
    });
}

function loadOnboarding() {
  fetch("/api/user/editor", {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      const title = document.getElementById("title-edit");
      title.textContent = "Welcome on 𝕐 !";
      const button = document.getElementById("exit-button");
      button.setAttribute("onclick", "loadPreferencesEditor()");
      button.textContent = "Continue";
      fetch(`/api/user/info/0`, {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          const picture = document.getElementById("picture-edit");
          const name = document.getElementById("displayname-edit");
          const description = document.getElementById("description-edit");
          const location = document.getElementById("location-edit");

          picture.src = `/static/pictures/${res.picture}.png`;
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
  fetch("/api/user/tags?user=true", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        const divTags = document.getElementById("selected-tags");
        divTags.innerHTML = "";
        for (var key in res.tags) {
          divTags.innerHTML += `
          <span class="subject-tag" id="tag-${res.tags[key]}">
          <i class="fa-solid fa-hashtag"></i>
          ${key}
          <div id="e"></div>
          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[key]})"></i>
        </span>`;
        }
      }
    });
}

function loadPreferencesEditor() {
  removeEditor();
  fetch("/api/user/preferences", {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      if (window.location.pathname.startsWith("/profile")) {
        const onClickOutside = (e) => {
          if (e.target.className.includes("layer")) {
            removeEditor();
            window.removeEventListener("click", onClickOutside);
          }
        };
        window.addEventListener("click", onClickOutside);
      }
      loadUserPreferenceEditor();
      fetch("/api/user/tags", {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          console.log(res);
          var tags = [];
          for (var key in res.tags) tags.push(key);
          if (res.code === "success") {
            $(function () {
              $("#subject-input").autocomplete({
                source: tags,
                select: function (event, ui) {
                  ui.item.value = ui.item.label;
                  $("#selected-tags").append(`
                        <span class="subject-tag" id="tag-${res.tags[ui.item.label]
                    }">
                          <i class="fa-solid fa-hashtag"></i>
                          ${ui.item.label}
                          <div id="e"></div>
                          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[ui.item.label]
                    })"></i>
                        </span>`);
                  $(this).val("");

                  return false;
                },
              });
            });
          }
        });
    });
}

function removeTag(id_tag) {
  var tag;
  if (id_tag.startsWith("tag-")) {
    tag = `${id_tag}`;
  } else {
    tag = `tag-${id_tag}`;
  }
  document.getElementById(tag).remove();
}

function selectTag() {
  if (document.getElementById("post-title")) {
    t = document.getElementById("post-title");
    stitle = t.value;
  }
  fetch("/api/user/preferences", {
    method: "GET",
  })
    .then((res) => res.text())
    .then((res) => {
      document.body.innerHTML += res;
      if (document.getElementById("post-title")) {
        t = document.getElementById("post-title");
        t.value = stitle;
      }
      const onClickOutside = (e) => {
        if (e.target.className.includes("layer")) {
          removeEditor();
          window.removeEventListener("click", onClickOutside);
        }
      };
      window.addEventListener("click", onClickOutside);

      document.getElementById("title-edit").textContent =
        "Choose tags to identify your post";
      button = document.getElementById("exit-button");
      button.textContent = "Save tags";
      button.setAttribute("onclick", "updateSelectedTags()");

      fetch("/api/user/tags", {
        method: "GET",
      })
        .then((res) => res.json())
        .then((res) => {
          console.log(res);
          var tags = [];
          for (var key in res.tags) tags.push(key);
          if (res.code === "success") {
            $(function () {
              $("#subject-input").autocomplete({
                source: tags,
                select: function (event, ui) {
                  ui.item.value = ui.item.label;
                  $("#selected-tags").append(`
                        <span class="subject-tag" id="tag-${res.tags[ui.item.label]
                    }">
                          <i class="fa-solid fa-hashtag"></i>
                          ${ui.item.label}
                          <div id="e"></div>
                          <i id="trash-remove" class="fa-solid fa-trash" onclick="removeTag(${res.tags[ui.item.label]
                    })"></i>
                        </span>`);
                  $(this).val("");

                  return false;
                },
              });
            });
          }
        });
    });
}

function updateSelectedTags() {
  const tagsDiv = document.getElementById("selected-tags");
  tagsRow = document.getElementById("tag-list");
  for (let i = 0; i < tagsDiv.children.length; i++) {
    tagsRow.innerHTML += `
    <div class="row" id="${tagsDiv.children[i].id}">
        <i class="fa-solid fa-hashtag"></i>
        ${tagsDiv.children[i].textContent}
        <i id="trash-remove" onclick="removeTag('${tagsDiv.children[i].id}')" class="fa-solid fa-trash"></i>
    </div>`;
  }
  removeEditor();
}

function savePreferences() {
  const tagsDiv = document.getElementById("selected-tags");
  const tags = [];
  for (let i = 0; i < tagsDiv.children.length; i++) {
    tags.push(tagsDiv.children[i].id);
  }
  console.log(tags);
  const data = new FormData();
  data.append("tags", tags);
  fetch("/api/user/tags/update", {
    method: "PATCH",
    body: data,
  })
    .then((res) => res.text())
    .then((res) => {
      console.log(res);
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

function updateSettings() {
  const email = document.getElementById("email-edit").value;
  const currentPassword = document.getElementById("currentpassword").value;
  const newPassword = document.getElementById("password").value;
  const newPasswordConfirm = document.getElementById("cpassword").value;

  if (email === "") {
    alert("Please enter an email adress to continue")
  } else if ((newPassword !== "" && newPasswordConfirm === "") || newPassword !== newPasswordConfirm) {
    alert("Please enter a new password to continue")
  } else {
    
    const data = new FormData();
    data.append("email",email)
    data.append("cpassword",currentPassword)
    data.append("npassword",newPasswordConfirm)

    fetch("/api/user/settings/update", {
      method: "PATCH",
      body: data,
    })
      .then((response) => response.text())
      .then((data) => {
        switch(data.trim()) {
          case "success":
            removeEditor();
            break;
          case "bad_password":
            alert("Wrong password entered")
            break;
          case "login":
            redirect("/login");
            break;
        }
      });
  }
}

function deleteAccount() {
  if (
    confirm(
      "Are you sure you want to delete your account ?\nThis action cannot be undone"
    ) && confirm("Last chance...")
  ) {
    password = prompt("Please enter your password to confirm")
    data = new FormData()
    data.append('password',password)
    fetch(`/api/user/delete`, {
      method: "DELETE",
      body: data
    })
      .then((res) => res.text())
      .then((res) => {
        switch(res.trim()) {
          case "success":
            alert("All your data has been deleted, you will now be redirected to the homepage")
            redirect("/home");
            break;
          case "bad_password":
            alert("Wrong password entered")
            break;
          case "login":
            redirect("/login");
            break;
        }
      });
  }
}

function updateProfile() {
  const name = document.getElementById("displayname-edit").value;
  let description = document.getElementById("description-edit").value;
  const location = document.getElementById("location-edit").value;
  const M = document.getElementById("male").checked;
  const F = document.getElementById("female").checked;
  var gender = "X";
  if (M) {
    gender = "M";
  } else if (F) {
    gender = "F";
  }

  description = description.replace(/\r?\n/g, "<br />");

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
        windows.location.href = "/login";
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
        .then((response) => response.json())
        .then((response) => {
          if (response.code == "success") {
            console.log("Profile picture updated successfully!");
            picture = document.getElementById("picture-edit");
            picture.src = `/static/pictures/${response.hash}.png`;
            loadUserMenu();
            loadUserProfile(0);
          } else {
            console.error("Error updating profile picture:", response.code);
            alert("Error updating profile picture:" + response.code);
          }
        })
        .catch((error) => {
          console.error("Error sending file:", error);
        });
    }
  };
  fileInput.click();
}

function loadUserFollowers(id_user) {
  document.getElementById("row3").remove();
  fetch(`/api/user/followers/${id_user}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      if (res.code === "success") {
        let row1 = document.getElementById("row1");
        row1.setAttribute("onClick", `redirect("/profile?id_user=${id_user}")`);
        var css = `
        .row#row1:hover {
          background-color: #FFFFFF;
          cursor:pointer;
          color: black;
        }`;
        var style = document.createElement("style");
        if (style.styleSheet) {
          style.styleSheet.cssText = css;
        } else {
          style.appendChild(document.createTextNode(css));
        }
        document.getElementsByTagName("head")[0].appendChild(style);
        let row2 = document.getElementById("row2");
        row2.setAttribute("class", "cell");
        row2.innerHTML = `
        <div class="row">
        <a href="/followers?id_user=${id_user}"><div class="row current-tab"><h2>Followers</h2></div></a>
        <a href="/following?id_user=${id_user}"><div class="row other-tab"><h2>Following</h2></div></a>
        </div>`;
        row2.innerHTML += `<div class="cell" id="follows"></div>`;
        follows = document.getElementById("follows");
        res.data.forEach(function (user) {
          desc = user.description === null ? "" : user.description;
          row = `
          <a href="/profile?id_user=${user.id}">
            <div class="user-row" id="follower-user-${user.id}">
              <img src="/static/pictures/${user.picture}.png">
              <div class="user-names">
                <b>${user.displayname}</b>
                <i>@${user.username}</i>
                <div class="row" id="description">
                ${desc}
                </div>
              </div>
              <div style="flex-grow:1"></div>
            </div>
          </a>
          <hr id="hr-${user.id}">
          `;
          follows.innerHTML += row;
        });
      }
    });
}

function loadUserFollowing(id_user) {
  document.getElementById("row3").remove();
  fetch(`/api/user/following/${id_user}`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((res) => {
      if (res.code === "success") {
        let row1 = document.getElementById("row1");
        row1.setAttribute("onClick", `redirect("/profile?id_user=${id_user}")`);
        var css = `
        .row#row1:hover {
          background-color: #FFFFFF;
          cursor:pointer;
          color: black;
        }`;
        var style = document.createElement("style");
        if (style.styleSheet) {
          style.styleSheet.cssText = css;
        } else {
          style.appendChild(document.createTextNode(css));
        }
        document.getElementsByTagName("head")[0].appendChild(style);
        let row2 = document.getElementById("row2");
        row2.setAttribute("class", "cell");
        row2.innerHTML = `
        <div class="row">
        <a href="/followers?id_user=${id_user}"><div class="row other-tab"><h2>Followers</h2></div></a>
        <a href="/following?id_user=${id_user}"><div class="row current-tab"><h2>Following</h2></div></a>
        </div>`;
        row2.innerHTML += `<div class="cell" id="follows"></div>`;
        follows = document.getElementById("follows");
        res.data.forEach(function (user) {
          desc = user.description === null ? "" : user.description;
          row = `
          <a href="/profile?id_user=${user.id}">
            <div class="user-row" id="following-user-${user.id}">
              <img src="/static/pictures/${user.picture}.png">
              <div class="user-names">
                <b>${user.displayname}</b>
                <i>@${user.username}</i>
                <div class="row" id="description">
                ${desc}
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

function sendNewPost(id_post) {
  postContent = getPostContent();
  title = document.getElementById("post-title").value;
  tagsElement = document.querySelectorAll('[id^="tag-"]');
  tags = [];
  tagsElement.forEach((tag) => {
    if (/^\d+$/.test(tag.id.slice(4))) {
      tags.push(tag.id);
    }
  });
  const data = new FormData();
  data.append("title", title);
  data.append("tags", tags);
  data.append("post", postContent);
  data.append("id_post", id_post);

  url = null;
  if (window.location.pathname.startsWith("/post/new")) {
    url = "/api/post/create";
  } else {
    url = `/api/post/edit?id_post=${id_post}`;
  }

  fetch(url, {
    method: "POST",
    body: data,
  })
    .then((res) => res.json())
    .then((res) => {
      console.log(res);
      if (res.code === "success") {
        window.location.href = "/post/view/" + res.post;
      }
    });
}

function loadPostEdition(id_post) {
  fetch(`/api/post/get/${id_post}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        document.getElementById("post-title").value = res.title;
        setPostContent(res.content);
        tagsRow = document.getElementById("tag-list");
        for (let i = 0; i < res.tags.length; i++) {
          tagsRow.innerHTML += `
          <div class="row" id="${res.id_tags[i]}">
              <i class="fa-solid fa-hashtag"></i>
              ${res.tags[i]}
              <i id="trash-remove" onclick="removeTag('${res.id_tags[i]}')" class="fa-solid fa-trash"></i>
          </div>`;
        }
      }
    });
}

function loadFeed(offset) {
  button = document.getElementById("load-more");
  if (button !== null) {
    button.remove();
  }

  filter = document.getElementById("filter").value;
  fetch(`/api/post/feed?f=${filter}&offset=${offset}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code == "success") {
        feed = document.getElementById("posts-feed");
        res.posts.forEach((post) => {
          feed.innerHTML += `
          <a href="/post/view/${post.id_post}">
              <div class="post-block">
                  <h2 id="post-title">${post.title}</h2>
                  <div id="post-author" onclick="event.preventDefault();redirect('/profile?id_user=${post.id_author
            }')">
                      <img src="/static/pictures/${post.author_picture}.png">
                      <h3>${post.author}, on ${post.created_at}</h3>
                  </div>
                  <div class="post-content ql-editor">
                  ${post.content}
                  </div>
                <div id="stats">
                  ${getStatsBar(post)}
                </div>
              </div>
          </a>`;
        });
        feed.innerHTML += `
        <button id="load-more" onclick="loadFeed(${offset + 10
          })">See more</button>
        `;
        document.querySelectorAll("pre").forEach((block) => {
          console.log(block);
          hljs.highlightElement(block);
        });
      } else {
        console.log(res);
      }
    });
}

function getStatsBar(res) {
  // likes
  likes = '<div class="row">';
  if (res.is_liked === true) {
    likes += `<i id="like-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'L-')" class="fa-solid fa-thumbs-up" style="color:green"></i>`;
  } else {
    likes += `<i id="like-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'L+')" class="fa-solid fa-thumbs-up"></i>`;
  }
  likes += `<p id='count-like-${res.id_post}'>${res.like}</p></div>`;

  // dislikes
  dislikes = '<div class="row">';
  if (res.is_disliked === true) {
    dislikes += `<i id="dislike-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'D-')" class="fa-solid fa-thumbs-down" style="color:red"></i>`;
  } else {
    dislikes += `<i id="dislike-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'D+')" class="fa-solid fa-thumbs-down"></i> `;
  }
  dislikes += `<p id='count-dislike-${res.id_post}'>${res.dislike}</p></div>`;

  // saved
  saved = '<div class="row">';
  if (res.is_saved === true) {
    saved += `<i id="save-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'S-')" class="fa-solid fa-bookmark" style="color:blue"></i>`;
  } else {
    saved += `<i id="save-button-${res.id_post}" onclick="event.preventDefault();actionPost(${res.id_post},'S+')" class="fa-solid fa-bookmark"></i> `;
  }
  saved += `<p id='count-saved-${res.id_post}'>${res.saved}</p></div>
  <div style="flex-grow:1;"></div>`;

  return likes + dislikes + saved;
}

function loadPost(id_post) {
  fetch(`/api/post/get/${id_post}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        document.title = res.title;
        document.getElementById("post-title").textContent = res.title;
        document.getElementById("post-author").innerHTML = `
        <a href="/profile?id_user=${res.id_author}">
          <img src="/static/pictures/${res.author_picture}.png">
          <h3>By ${res.author}, on ${res.created_at}</h3>
        </a>`;
        document.getElementById("post-content").innerHTML = res.content;
        stats = document.getElementById(`stats-${id_post}`);

        stats.innerHTML = getStatsBar(res);
        tagsDiv = document.getElementById("tag-list");
        tagsDiv.innerHTML = "";
        res.tags.forEach((tag) => {
          tagsDiv.innerHTML += `
        <div class="row">
        <i class="fa-solid fa-hashtag"></i>
        ${tag}
        </div>`;
        });

        if (
          res.is_logged == "yes" &&
          window.location.pathname.startsWith("/post/view")
        ) {
          stats.innerHTML += `
          <button class="edit-post-button" onclick="redirect('/post/edit?id_post=${id_post}')">Edit your post</button>
          <button id="remove-post" class="edit-post-button" onclick="deletePost('${id_post}')">Delete your post</button>
          `;
        }

        document.querySelectorAll("pre").forEach((block) => {
          hljs.highlightElement(block);
        });
      }
    });
}

function actionPost(id_post, action) {
  fetch(
    `/api/post/action?id_post=${id_post}&action=${encodeURIComponent(action)}`,
    {
      method: "PATCH",
    }
  )
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        if (window / location.pathname.startsWith("/post/view")) {
          loadPost(id_post);
        } else {
          switch (action) {
            case "L+":
              e = document.getElementById(`like-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'L-')`
              );
              e.style.color = "green";
              count = document.getElementById(`count-like-${id_post}`);
              count.textContent = Number(count.textContent) + 1;
              break;
            case "L-":
              e = document.getElementById(`like-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'L+')`
              );
              e.style.color = "white";
              count = document.getElementById(`count-like-${id_post}`);
              count.textContent = Number(count.textContent) - 1;
              break;
            case "D+":
              e = document.getElementById(`dislike-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'D-')`
              );
              e.style.color = "red";
              count = document.getElementById(`count-dislike-${id_post}`);
              count.textContent = Number(count.textContent) + 1;
              break;
            case "D-":
              e = document.getElementById(`dislike-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'D+')`
              );
              e.style.color = "white";
              count = document.getElementById(`count-dislike-${id_post}`);
              count.textContent = Number(count.textContent) - 1;
              break;
            case "S+":
              e = document.getElementById(`save-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'S-')`
              );
              e.style.color = "blue";
              count = document.getElementById(`count-saved-${id_post}`);
              count.textContent = Number(count.textContent) + 1;
              break;
            case "S-":
              e = document.getElementById(`save-button-${id_post}`);
              e.setAttribute(
                "onclick",
                `event.preventDefault();actionPost(${id_post},'S+')`
              );
              e.style.color = "white";
              count = document.getElementById(`count-saved-${id_post}`);
              count.textContent = Number(count.textContent) - 1;
              break;
          }
        }
      } else {
        console.log(res);
      }
    });
}

function deletePost(id_post) {
  if (
    confirm(
      "Are you sure you want to delete your post ?\nThis action cannot be undone"
    )
  ) {
    fetch(`/api/post/delete?id_post=${id_post}`, {
      method: "DELETE",
    })
      .then((res) => res.text())
      .then((res) => {
        if (res === "success") {
          redirect("/home");
        } else {
          console.log(res);
        }
      });
  }
}

function loadComments(id_post) {
  fetch(`/api/post/comment/get?id_post=${id_post}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        comments = document.getElementById("comments");
        comments.innerHTML = "";
        res.comments.forEach((comment) => {
          content = `
          <div class="comment">
            <div id="comment-author" onclick="event.preventDefault();redirect('/profile?id_user=${comment.id_author}')">
              <img src="/static/pictures/${comment.author_picture}.png">
              <h3>By ${comment.author}, on ${comment.created_at}</h3>
            </div>
            ${comment.content}`;
          if (comment.is_author === "yes") {
            content += `</br><button id="remove-comment" onclick="deleteComment(${comment.id_comment},${id_post})">remove</button>`;
          }
          content += "</div>";
          comments.innerHTML += content;
        });
      } else {
        console.log(res);
      }
    });
}

function sendComment(id_post) {
  inp = document.getElementById("comment-input");
  content = inp.value;
  inp.value = "";

  data = new FormData();
  data.append("post", id_post);
  data.append("content", content);

  fetch("/api/post/comment/add", {
    method: "POST",
    body: data,
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        loadComments(id_post);
      } else {
        console.log(res);
      }
    });
}

function deleteComment(id_comment, id_post) {
  if (
    confirm(
      "Are you sure you want to delete your comment ?\nThis action cannot be undone"
    )
  ) {
    fetch(`/api/post/comment/delete?id_comment=${id_comment}`, {
      method: "DELETE",
    })
      .then((res) => res.text())
      .then((res) => {
        if (res === "success") {
          loadComments(id_post);
        } else {
          console.log(res);
        }
      });
  }
}

function loadConversations(conversation = "none") {
  fetch("/api/messages/get/all", {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        conv = document.getElementById("conversations");
        conv.innerHTML = "";
        isfirst = true;
        first_id = 0;
        res.conv.forEach((contact) => {
          time = contact.last_time.split(" ");
          row = "";
          if (isfirst) {
            isfirst = false;
            first_id = contact.id_contact;
            row = `<div id="contact-${contact.id_contact}" class="row focused" onclick="loadConversation(${contact.id_contact})">`;
          } else {
            row = `<div id="contact-${contact.id_contact}" class="row" onclick="loadConversation(${contact.id_contact})">`;
          }
          row += `
            <img src="/static/pictures/${contact.contact_picture}.png">
            <div class="cell">
              <h3>${contact.contact}</h3>
              <i>Last on ${time[0]}<br>at ${time[1]}</i>
            </div>
          </div>
          `;
          conv.innerHTML += row;
        });
        conv.innerHTML += '<div style="flex-grow:1"></div>';
        if (conversation !== "none") {
          loadConversation(conversation);
        } else {
          loadConversation(first_id);
        }
      } else {
        console.log(res);
      }
    });
}

function loadConversation(contact) {
  fetch(`/api/messages/get?contact=${contact}`, {
    method: "GET",
  })
    .then((res) => res.json())
    .then((res) => {
      if (res.code === "success") {
        container = document.getElementById("message");
        container.innerHTML = "";
        messages = res.messages;
        isFirst = true;

        document.querySelectorAll(".focused").forEach((div) => {
          div.classList.remove("focused");
        });
        newFocus = document.getElementById(`contact-${contact}`);
        if (newFocus) {
          newFocus.classList.add("focused");
        } else {
          conv = document.getElementById("conversations");
          existingConv = conv.innerHTML;
          conv.innerHTML =
            `
          <div id="contact-${res.id_contact}" class="row focused" onclick="loadConversation(${res.id_contact})">
          <img src="/static/pictures/${res.contact_picture}.png">
            <div class="cell">
              <h3>${res.contact}</h3>
              <i>Draft</i>
            </div>
          </div>` + existingConv;
        }

        for (i = 0; i < messages.length; i++) {
          row = "";
          from = messages[i].from;

          next = i + 1 < messages.length ? messages[i + 1].from : false;
          previous = i - 1 >= 0 ? messages[i - 1].from : false;

          if (
            (previous !== from && previous) ||
            (from !== next && next && !previous) ||
            isFirst
          ) {
            isFirst = false;
            picture =
              from === res.id_user ? res.user_picture : res.contact_picture;
            username = from === res.id_user ? res.user : res.contact;
            row = `
            <div class="row">
              <img src="/static/pictures/${picture}.png" onclick="redirect('/profile?id_user=${from}')">
              <div class="name-date">
              <h3>${username}</h3>
              <i>on ${messages[i].time}</i>
              </div>
            </div>`;
          }
          if (messages[i].owner === "yes") {
            row += `<div id="message-${messages[i].id_message}" onmouseenter="showDeleteMessage('${messages[i].id_message}')" onmouseleave="hideDeleteMessage('${messages[i].id_message}')" >
                <p>> ${messages[i].message}</p>
                <div id="delete-${messages[i].id_message}" class="delete-row" onclick="deleteMessage(${messages[i].id_message})">
                  <i class="fa-solid fa-trash"></i>
                  Delete message ?
                </div>
              </div>
            `;
          } else {
            row += `
            <p>> ${messages[i].message}</p>
            `;
          }
          container.innerHTML += row;
        }
        container.scrollTop = container.scrollHeight;
      } else {
        console.log(res);
      }
    });
}

function sendMessage() {
  id = document.querySelectorAll(".focused")[0].getAttribute("id");
  contact = id.replace("contact-", "");

  input = document.getElementById("message-input");
  message = input.value;
  message = message.replace(/\r?\n/g, "<br />");
  input.value = "";

  data = new FormData();
  data.append("contact", contact);
  data.append("message", message);
  fetch(`/api/messages/send`, {
    method: "POST",
    body: data,
  })
    .then((res) => res.text())
    .then((res) => {
      if (res === "success") {
        loadConversations();
      } else {
        console.log(res);
      }
    });
}

function toggleRefresh(interval = null) {
  button = document.getElementById("toggle-button");
  if (interval !== null) {
    clearInterval(interval);
    button.setAttribute("onclick", `toggleRefresh()`);
    button.textContent = "Auto-Refresh off";
    button.style.backgroundColor = "#aa2d2d";
  } else {
    interval = setInterval(function () {
      id = document.querySelectorAll(".focused")[0].getAttribute("id");
      contact = id.replace("contact-", "");
      loadConversation(contact);
    }, 1000);
    button.setAttribute("onclick", `toggleRefresh(${interval})`);
    button.textContent = "Auto-Refresh on";
    button.style.backgroundColor = "green";
  }
}

function showDeleteMessage(id_message) {
  deleteElement = document.getElementById(`delete-${id_message}`);
  deleteElement.style.display = "block";
}

function hideDeleteMessage(id_message) {
  deleteElement = document.getElementById(`delete-${id_message}`);
  deleteElement.style.display = "none";
}

function deleteMessage(id_message) {
  if (
    confirm(
      "Are you sure you want to delete your message ?\nThis action cannot be undone"
    )
  ) {
    fetch(`/api/messages/delete?id_message=${id_message}`, {
      method: "DELETE",
    })
      .then((res) => res.text())
      .then((res) => {
        if (res === "success") {
          document.getElementById(`message-${id_message}`).remove();
        } else {
          console.log(res);
        }
      });
  }
}
