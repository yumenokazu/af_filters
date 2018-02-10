from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from filter_app.app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand) # 'db' is the command's name


if __name__ == '__main__':
    manager.run()

'''
manage.py db init
manage.py db migrate --message MESSAGE
manage.py db upgrade
'''