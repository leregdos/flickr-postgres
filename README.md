# flickr-postgres

This is a Flask + PostgreSQL implementation of a picture sharing social media platform, similar to Instagram or Flickr.

## Instructions to run the project

### Requirements

1. Python

### Dependencies

1. Run `pip install -r requirements.txt` to install all dependencies in the virtual environment.

### Database

To set up the local database, from the root folder, do the following:

1. CD into `database` directory: `CD database`
2. Run psql interactive mode: `psql postgres`
3. Create new user: `CREATE USER username WITH PASSWORD 'pass';`
4. Create new database: `CREATE DATABASE flickr_postgres;`
5. Create the tables: `\i define_schema.sql`
6. Exit the interactive mode: `\q`

## Acknolwedgements

- The html templates were taken from this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login)
