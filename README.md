# Example project

## Setup guide

### Tailwind
Reference: https://tailwindcss.com/docs/installation
1. `npm install -D tailwindcss`: Add tailwindcss as a dev dependency.
1. `npx tailwindcss init`: Create tailwind.config.js
1. `npx tailwindcss -i ./input.css -o ./static/css/main.css --watch`: Generate stylesheets (use `--watch` to monitor changes to templates and update `main.css` accordingly)

Proceed from step 3 (Generate stylesheets) on existing projects where the necessary config files have already been created.

### Sass
Reference: https://sass-lang.com/install/
1. `npm install -g sass`: Add Sass as a command line tool.
1. `sass --watch scss/battleship.scss:static/css/battleship.css`: Compile custom stylesheets for Battleship graphics, using `--watch` to monitor changes.

Proceed from step 2 (Compile custom stylesheets) on existing installations.

### HTMX
Reference: https://htmx.org

No set up required for now. Future work may involve vendoring the HTMX dependency.

### Flask
Reference: https://flask-htmx.readthedocs.io/en/latest/quickstart.html

#### Setup
1. `python3 -m venv venv`: Create new virtual environment at relative path `venv`. Replace `python3` with the relevant command on your system, i.e. `py` or `python`.
1. Enter your newly created virtual environment: VS Code should detect this for you and enter `venv` after restarting terminal. To do this manually, run the following:
```source venv/bin/activate```
1. `python3 -m pip install -r requirements.txt`: Install packages required to run application. Invoking `pip` as a Python module avoids issues related to having separate or missing Python installs, such as after an update.

#### Development
This will invoke `app.create_app()`, and attempt to load data from [TinyDb](https://tinydb.readthedocs.io/en/latest/index.html)
1. `flask run --debug`: Launch the application in debug mode.

#### Production
The production site is deployed and run on Google Cloud, loading data from Cloud Storage. To test locally, Application Default Credentials (ADC) must be set up.

See the following guide: https://cloud.google.com/docs/authentication/application-default-credentials#personal
1. Substitute with `source .env && python3 -m gunicorn --bind :$PORT gcp:app` to test production configuration.

## Project structure
This repository is arranged to support running Flask with default configuration. Flask makes use of the following directories:
- `static`: used for serving static content, such as CSS stylesheets.
- `templates`: used for sourcing templates named in `render_template` calls.
