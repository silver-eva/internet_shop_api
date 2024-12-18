create schema if not exists app;

create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;
create type app.roles as enum('admin', 'writer', 'viewer');

-- auto encryption user password function
create or replace function encrypt_password()
returns trigger as $$
begin
	new.password = crypt(new.password, gen_salt('bf'));
  return new;
end;
$$ language plpgsql;

-- autoupdate updated field function
-- create or replace function update_updated()
-- returns trigger as $$
-- begin
-- 	new.updated = now();
--   return new;
-- end;
-- $$ language plpgsql;

-- creating the user table with auto UUID as PK: 
create table app.user (
  id uuid primary key not null DEFAULT uuid_generate_v4(),
  name varchar(128) not null unique,
  password text not null,
  email varchar(255) not null unique,
  created timestamp default now(),
  updated timestamp default now(),
  role app.roles not null default 'viewer'
);

-- user email validation
alter table app.user
add constraint email_format check (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- autoencrypt user password on insert
create or replace trigger encrypt_password_before_insert
before insert on app.user
for each row
execute function encrypt_password();

-- -- autoupdate user updated on unpdate
-- create or replace trigger update_user_updated_on_update
-- before update on app.user
-- for each row
-- execute function update_updated();

insert into app.user (name, password, email, role) values ('admin', 'admin', 'oMq7W@example.com', 'admin');

-- create table app.item (
--   id uuid primary key not null DEFAULT uuid_generate_v4(),
--   name varchar(128) not null,
--   created timestamp default now(),
--   updated timestamp default now()
-- );