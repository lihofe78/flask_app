CREATE TABLE IF NOT EXISTS  Images (
    id INTEGER PRIMARY KEY,
    name TEXT,
    image_file TEXT
);

CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
time integer NOT NULL
);


CREATE TABLE IF NOT EXISTS Image_Category (
    id INTEGER PRIMARY KEY,
    image_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY (image_id) REFERENCES Images(id),
    FOREIGN KEY (category_id) REFERENCES Categories(id)
);
