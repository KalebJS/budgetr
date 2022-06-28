DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categorical_mapping;
DROP TABLE IF EXISTS categories;

CREATE TABLE user
(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL
);

CREATE TABLE transactions
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER   NOT NULL,
    created     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title       TEXT      NOT NULL,
    value       INT       NOT NULL,
    category_id INT       NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

create table categorical_mapping
(
    id             integer not null
        constraint categorical_mapping_pk
            primary key autoincrement,
    word           text    not null,
    categories     json    not null
);

create unique index categorical_mapping_id_uindex
    on categorical_mapping (id);

create table categories
(
    id               integer not null
        constraint categories_pk
            primary key autoincrement,
    label            text    not null,
    is_expense       integer not null,
    is_annual        integer not null,
    is_discretionary integer not null
);

create unique index categories_id_uindex
    on categories (id);

create unique index categories_label_uindex
    on categories (label);

insert into categories (id, label, is_expense, is_annual, is_discretionary)
values (-1, 'Unknown', 0, 0, 0);

insert into categories (id, label, is_expense, is_annual, is_discretionary)
values (0, 'Income', 0, 0, 0);
