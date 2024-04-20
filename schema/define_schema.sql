CREATE TABLE Users(
	-- auto incrementing id, automatic not null constraint
	user_id SERIAL,
	first_name VARCHAR(30),
	last_name VARCHAR(30),
	email VARCHAR(30),
	date_of_birth DATE,
	hometown VARCHAR(30),
	gender CHAR(1),
	password VARCHAR(255),
	UNIQUE (email),
	PRIMARY KEY (user_id),
);

CREATE TABLE Friends(
	user1_id INTEGER,
	user2_id INTEGER,
	FOREIGN KEY (user1_id) REFERENCES Users(user_id),
	FOREIGN KEY (user2_id) REFERENCES Users(user_id),
	PRIMARY KEY (user1_id, user2_id)
);

CREATE TABLE Albums(
	album_id SERIAL,
	name VARCHAR(30),
	owner INTEGER,
	date_of_creation DATE,
	FOREIGN KEY (owner) REFERENCES Users(user_id),
	PRIMARY KEY (album_id)
);

CREATE TABLE Photos(
	photo_id INTEGER,
	caption VARCHAR(100),
	-- # as a path to the photo
	data VARCHAR(255),
	album_id INTEGER,
	-- delete photos in an album if the album is deleted
	FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
	PRIMARY KEY photo_id
);

CREATE TABLE Tags(
	tag_id INTEGER,
	words VARCHAR(50),
	PRIMARY KEY tag_id
);

CREATE TABLE Tagged(
	tag_id INTEGER,
	photo_id INTEGER,
	FOREIGN KEY (tag_id) REFERENCES Tags(tag_id),
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id),
	PRIMARY KEY (tag_id, photo_id)
);

CREATE TABLE Comments(
	comment_id INTEGER,
	owner INTEGER,
	posted_date DATE,
	FOREIGN KEY (owner) REFERENCES Users(user_id),
	PRIMARY KEY (comment_id)
);

CREATE TABLE Likes(
	user_id INTEGER,
	photo_id INTEGER,
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id),
	PRIMARY KEY (user_id, photo_id)
)