CREATE TABLE `users` (
  `id_user` INTEGER PRIMARY KEY,
  `username` varchar(255),
  `displayname` varchar(255),
  `email` varchar(255),
  `password` text,
  `role` text,
  `description` text,
  `created_at` timestamp,
  `last_update` timestamp,
  `gender` char,
  `notification` char
);

CREATE TABLE `profil_pictures` (
  `id_image` varchar(255) PRIMARY KEY,
  `user` INTEGER
);

CREATE TABLE `sessions` (
  `id_user` INTEGER,
  `token` text
);

CREATE TABLE `user_tags` (
  `user` INTEGER,
  `tag` INTEGER
);

CREATE TABLE `tags` (
  `id_tag` INTEGER PRIMARY KEY,
  `name` text
);

CREATE TABLE `relations` (
  `id_relation` INTEGER PRIMARY KEY,
  `followed` INTEGER,
  `follower` INTEGER
);

CREATE TABLE `posts` (
  `id_post` INTEGER PRIMARY KEY,
  `author` INTEGER,
  `title` text,
  `content` text,
  `like` INTEGER,
  `dislike` INTEGER,
  `comments` INTEGER
);

CREATE TABLE `posts_interaction` (
  `post` INTEGER,
  `user` INTEGER,
  `action` char
);

CREATE TABLE `comments` (
  `id_comment` INTEGER PRIMARY KEY,
  `parent` INTEGER,
  `author` INTEGER,
  `content` text,
  `like` text,
  `dislike` text
);

ALTER TABLE `profil_pictures` ADD FOREIGN KEY (`user`) REFERENCES `users` (`id_user`);

ALTER TABLE `sessions` ADD FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`);

ALTER TABLE `user_tags` ADD FOREIGN KEY (`tag`) REFERENCES `tags` (`id_tag`);

ALTER TABLE `user_tags` ADD FOREIGN KEY (`user`) REFERENCES `users` (`id_user`);

ALTER TABLE `relations` ADD FOREIGN KEY (`followed`) REFERENCES `users` (`id_user`);

ALTER TABLE `relations` ADD FOREIGN KEY (`follower`) REFERENCES `users` (`id_user`);

ALTER TABLE `posts` ADD FOREIGN KEY (`author`) REFERENCES `users` (`id_user`);

ALTER TABLE `comments` ADD FOREIGN KEY (`parent`) REFERENCES `posts` (`id_post`);

ALTER TABLE `comments` ADD FOREIGN KEY (`parent`) REFERENCES `comments` (`id_comment`);

ALTER TABLE `comments` ADD FOREIGN KEY (`author`) REFERENCES `users` (`id_user`);

ALTER TABLE `posts_interaction` ADD FOREIGN KEY (`user`) REFERENCES `users` (`id_user`);

ALTER TABLE `posts_interaction` ADD FOREIGN KEY (`post`) REFERENCES `posts` (`id_post`);