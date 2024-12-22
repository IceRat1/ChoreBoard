DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS user_groups;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE user_groups (
    userid INTEGER NOT NULL,
    groupid INTEGER NOT NULL,
    PRIMARY KEY (userid, groupid),
    FOREIGN KEY (userid) REFERENCES user (id),
    FOREIGN KEY (groupid) REFERENCES groups (id)
);

