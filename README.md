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

## Notes from Chunting 
### On Photo Management
1. Need to recreate the schema as I edit some parts.
2. User can go to the photos tab in the navigation bar to browse albums and photos from all user. 
3. Registered user can create new album from their profile page. Here the assumption is that each photo must be attached to an album, so they can only upload photo after the album is created.
4. Registered user can click the album they created (from their profile page or by clicking the album name on the photos page), and they will find a link that bring them to the form to upload photo to this album. 
5. Registered users can delete the photos and albums they created, but they cannot delete the ones created by other users.

### On Comments Function
1. Since it's not specified in the project description, we assume that only registered user can like a photo. 
2. On the other hand, as specified in the project description, both registered and unregisterd users can comment on a post. Unregistered users' comments will shown as by "Guest User".
3. As stated in the project description, the search comments function can only find comments that exactly match the input query. 



