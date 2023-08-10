# New HKN Portal

## Set up instructions for local development

- Clone the repository
- (Recommended) Create a virtualenv ([Instructions](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/))
  - Try to name the virtualenv venv as that name has been added in gitignore
  - Activate the virtualenv (Note - Make sure to always activate the virtualenv before working with new terminals)
- Run `pip install -r requirements.txt` to install all of the required libraries
- Run `poetry run python manage.py runserver` to start the django server
- Open a new terminal and activate the virtualenv
- Run `cd frontend && npm install`
  - Debug any issues that may come up regarding npm or node versions
- Run `npm run dev` to start the development server

You should now be set up to develop locally. Go to localhost:8000 on a borwser and you should see the portal hosted locally. Changes should automatically show on the server and there's no need to re-run the server unless you install new packages.

The portal was set up following these steps - https://dev.to/besil/my-django-svelte-setup-for-fullstack-development-3an8