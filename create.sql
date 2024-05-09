CREATE TABLE `users` (
  `id_user` int AUTO_INCREMENT PRIMARY KEY,
  `username` varchar(255),
  `email` varchar(255),
  `password` text,
  `role` text,
  `description` text,
  `created_at` timestamp,
  `last_update` timestamp,
  `gender` char,
  `notification` char
);

CREATE TABLE `user_tags` (
  `user` int,
  `tag` int
);

CREATE TABLE `tags` (
  `id_tag` int AUTO_INCREMENT PRIMARY KEY,
  `name` text
);

CREATE TABLE `relations` (
  `id_relation` int AUTO_INCREMENT PRIMARY KEY,
  `followed` int,
  `follower` int
);

CREATE TABLE `posts` (
  `id_post` int AUTO_INCREMENT PRIMARY KEY,
  `author` int,
  `title` text,
  `content` text,
  `like` int,
  `dislike` int,
  `comments` int
);

CREATE TABLE `comments` (
  `id_comment` int AUTO_INCREMENT PRIMARY KEY,
  `parent` int,
  `author` int,
  `content` text,
  `like` text,
  `dislike` text
);

ALTER TABLE `user_tags` ADD FOREIGN KEY (`tag`) REFERENCES `tags` (`id_tag`);

ALTER TABLE `user_tags` ADD FOREIGN KEY (`user`) REFERENCES `users` (`id_user`);

ALTER TABLE `relations` ADD FOREIGN KEY (`followed`) REFERENCES `users` (`id_user`);

ALTER TABLE `relations` ADD FOREIGN KEY (`follower`) REFERENCES `users` (`id_user`);

ALTER TABLE `posts` ADD FOREIGN KEY (`author`) REFERENCES `users` (`id_user`);

ALTER TABLE `comments` ADD FOREIGN KEY (`author`) REFERENCES `users` (`id_user`);
