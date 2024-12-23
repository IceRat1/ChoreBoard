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
    score INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (userid, groupid),
    FOREIGN KEY (userid) REFERENCES user (id),
    FOREIGN KEY (groupid) REFERENCES groups (id)
);

CREATE TABLE chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    reward INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);

CREATE TABLE user_chores (
    userid INTEGER NOT NULL,
    choreid INTEGER NOT NULL,
    PRIMARY KEY (userid, choreid),
    FOREIGN KEY (userid) REFERENCES user (id),
    FOREIGN KEY (choreid) REFERENCES chores (id)
)


