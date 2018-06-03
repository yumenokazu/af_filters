from filter_app import views, models
from filter_app.gsheets import price_task
from filter_app.app import app

if __name__ == '__main__':
    app.run(use_reloader=False)