# MDCalc--MIT

This is a risk calculator to predict the likelihood of Aortic Valve Stenosis.

## Installation

Make sure you are on Python 3 (`python --version`). The models included here are pickled with Python 3 and will not work with Python 2.

Make sure you have `pip` installed (`which pip`), and install requirements.txt:

```
pip install -r requirements.txt
```

## Running the App

Make sure you have installed Flask as above, and run:

```
FLASK_APP=app.py flask run
```

This will run the app at http://localhost:5000.

## Adding/Extending

The UI is built with [Semantic UI](https://semantic-ui.com/introduction/getting-started.html) for ease of use.

It uses some JQuery functions to toggle button colors and submit data to the model.

Finally, it uses [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/) to provide a simple JSON API to access the models.

## Deploying/Making Live

The app is set up for 1-click deploys to [Heroku](https://heroku.com).

If you'd like to deploy to your own Heroku account, [here](https://medium.com/@gitaumoses4/deploying-a-flask-application-on-heroku-e509e5c76524) is a short and sweet tutorial.
