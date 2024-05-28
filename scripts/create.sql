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
  `notification` char,
  `picture` varchar(255),
  `location` varchar(255)
);

CREATE TABLE `sessions` (
  `id_user` INTEGER,
  `token` text
);

CREATE TABLE `user_tags` (
  `user` INTEGER,
  `tag` INTEGER
);

CREATE TABLE `post_tags` (
  `post` INTEGER,
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
  `visibility` INTEGER,
  `title` text,
  `content` text,
  `created_at` timestamp
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
  `created_at` timestamp,
  `like` text,
  `dislike` text
);

CREATE TABLE `messages` (
  `id_conversation` INTEGER PRIMARY KEY,
  `from` INTEGER,
  `to` INTEGER,
  `time` timestamp,
  `message` text,
  `isread` char
);
