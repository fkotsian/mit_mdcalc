# MDCalc--MIT

This is a risk calculator to predict the likelihood of Aortic Valve Stenosis.

## Installation

Make sure you are on Python 3 (`python --version`). The models included here are pickled with Python 3 and will not work with Python 2.

Make sure you have `pip` installed (`which pip`), and install requirements.txt:

```
pip install -r requirements.txt
```

## Running the App on Your Computer

Make sure you have installed Flask as above, and run:

```
FLASK_ENV=development FLASK_APP=app.py flask run
```

This will run the app at http://localhost:5000.


## Running AS vs RLRVI

The calculator displayed is governed by a ENV variable named 'CALC_NAME'. 

This is read in app.py.

To change which calculator is displayed in DEVELOPMENT mode, change the CALC_NAME variable to the desired calculator:

  - CALC_NAME = 'as'    -> runs the AS calculator
  - CALC_NAME = 'rlrvi' -> runs the RLRVI calculator

## Making Changes to the lr_model scripts

To make a change to the lr_model.py scripts, simply copy the file over from Dropbox.

You may have to update the load paths to load from the appropriate folders (e.g., "model_rlrvi/norm_fact.pkl", "model_as/lr_model.pkl").

Test the app locally using the steps above to make sure the new lr_model script runs as expected.

Commit the changes to git, and push up to Github (`git commit -m "<a note about your changes>"`, `git push origin master`).

Your changes will deploy live to the site URL within 3-5 minutes.

## Adding/Extending

The UI is built with [Semantic UI](https://semantic-ui.com/introduction/getting-started.html) for ease of use.

It uses some JQuery functions to toggle button colors and submit data to the model.

Finally, it uses [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/) to provide a simple JSON API to access the models.

## Deploying/Making Live

The app is set up for 1-click deploys to [Heroku](https://heroku.com).

As soon as you push to the `master` branch of this repo, the changes should start deploying to Heroku, and you should see them live at the site URL within 3-5 minutes.

If you'd like to deploy to your own Heroku account, [here](https://medium.com/@gitaumoses4/deploying-a-flask-application-on-heroku-e509e5c76524) is a short and sweet tutorial.
