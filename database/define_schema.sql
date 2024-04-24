CREATE TABLE Users(
	-- auto incrementing id, automatic not null constraint
	user_id SERIAL,
	first_name VARCHAR(30) NOT NULL,
	last_name VARCHAR(30) NOT NULL,
	email VARCHAR(30) UNIQUE NOT NULL,
	date_of_birth DATE,
	hometown VARCHAR(30),
	gender CHAR(1),
	password VARCHAR(255),
	PRIMARY KEY (user_id)
);

CREATE TABLE Friends(
	user1_id INTEGER,
	user2_id INTEGER,
	-- delete the tuple if either user is deleted
	FOREIGN KEY (user1_id) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (user2_id) REFERENCES Users(user_id) ON DELETE CASCADE,
	PRIMARY KEY (user1_id, user2_id),
	CHECK (user1_id <> user2_id)
);

CREATE TABLE Albums(
	album_id SERIAL,
	name VARCHAR(30) NOT NULL,
	owner INTEGER NOT NULL,
	date_of_creation DATE NOT NULL,
	-- delete the album if the user is deleted
	FOREIGN KEY (owner) REFERENCES Users(user_id) ON DELETE CASCADE,
	PRIMARY KEY (album_id)
);

CREATE TABLE Photos(
	photo_id SERIAL,
	caption VARCHAR(255),
	-- # base 64
	data BYTEA NOT NULL,
	album_id INTEGER,
	-- delete photos in an album if the album is deleted
	FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
	PRIMARY KEY (photo_id)
);

CREATE TABLE Tags(
	tag_id SERIAL,
	words VARCHAR(50) UNIQUE,
	PRIMARY KEY (tag_id)
);

CREATE TABLE Tagged(
	tag_id INTEGER,
	photo_id INTEGER,
	FOREIGN KEY (tag_id) REFERENCES Tags(tag_id) ON DELETE CASCADE,
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE,
	PRIMARY KEY (tag_id, photo_id)
);

CREATE TABLE Comments(
	comment_id SERIAL,
	owner INTEGER NOT NULL,
	photo_id INTEGER NOT NULL,
	date DATE NOT NULL DEFAULT CURRENT_DATE,
	FOREIGN KEY (owner) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE,
	PRIMARY KEY (comment_id)
);

CREATE TABLE Likes(
	user_id INTEGER,
	photo_id INTEGER,
	FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE,
	PRIMARY KEY (user_id, photo_id)
);