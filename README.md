# New HKN Portal

## Set up instructions for local development

- Clone the repository
- (Recommended) Create a virtualenv ([Instructions](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/))
  - Try to name the virtualenv venv as that name has been added in gitignore
  - Activate the virtualenv (Note - Make sure to always activate the virtualenv before working with new terminals)
- Run `pip install -r requirements.txt` to install all of the required libraries
- Run the following commands to set up the database
  - Run `python manage.py makemigrations api` to create new migrations
  - Run `python manage.py migrate` to set up the database
  - Run `python manage.py create_groups` to create groups in the database
- Run ` python manage.py runserver` to start the django server
- Open a new terminal and activate the virtualenv
- Run `cd frontend && npm install`
  - Debug any issues that may come up regarding npm or node versions
- Run `npm run dev` to start the development server

You should now be set up to develop locally. Go to localhost:8000 on a browser and you should see the portal hosted locally. Changes should automatically show on the server and there's no need to re-run the server unless you install new packages.

If you are pulling changes that affect the database, run:
- Run `rm -r myapp/api/migrations` to remove the existing migrations folder
- Run `python manage.py makemigrations api` to create new migrations
- Run `python manage.py migrate` to set up the database
- Run `python manage.py create_groups` to create groups in the database

Custom `python manage.py` commands:
- `createsuperuser` creates a superuser
- `generate_inductees` generates a json file containing emails of inductees
- `induct file.json` induct inductees (change their role to members)
  - JSON file format is [{"email": "example@domain.com"}]
- `promote_officer file.json` promotes members to officers
  - JSON file format is [{"email": "example@domain.com", "position": "position"}]
- `newinductionclass` creates a new induction class object & related event for points rollover
-  `inducteeform` generates a new url for inductee forms based on current induction class