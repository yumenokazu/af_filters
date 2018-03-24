from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
# app.config.from_object('config.ProductionConfig')
# app.config.from_envvar('APPLICATION_SETTINGS', silent = True) # load another config if variable is EXPORTED

db = SQLAlchemy(app)

from filter_app import views, models
from filter_app.gsheets import price_task

if __name__ == '__main__':

    app.run(use_reloader=False)



