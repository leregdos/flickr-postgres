# flickr-postgres

This is a Flask + PostgreSQL implementation of a picture sharing social media platform, similar to Instagram or Flickr.

## Instructions to run the project

### Requirements

1. Python
2. [Virtualenv](https://virtualenv.pypa.io/en/latest/)

### Dependencies

To set up the dependencies, from the root folder, do the following (We assume that you have already installed virtualenv and activated your virtual environment):

1. Run `pip install -r requirements.txt` (or `pip3 install -r requirements.txt` if using python3) to install all dependencies in the virtual environment.

### Database

To set up the local database, from the root folder, do the following:

1. CD into `database` directory: `CD database`
2. Run psql interactive mode: `psql postgres`
3. Create new user: `CREATE ROLE username WITH LOGIN SUPERUSER PASSWORD 'pass';`
4. Create new database: `CREATE DATABASE flickr_postgres;`
5. Connect to database: `\c flickr_postgres`
6. Create the tables: `\i define_schema.sql`
7. Exit the interactive mode: `\q`

### Running the application

Run 'python3 app.py' in the root directory.

## Acknolwedgements

- The html templates were taken from this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login)
