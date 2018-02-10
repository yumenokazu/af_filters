import typing
import re

import flask_sqlalchemy
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from filter_app.app import db
import logging


def insert(db_obj: db.Model, db: SQLAlchemy) -> typing.NoReturn:
    '''
    inserts single db_obj into db
    '''
    if type(db_obj) == db.Model:
        try:
            db.session.add(db_obj)
            db.session.commit()
        except Exception as e:
            logging.exception(e, exc_info=True)


def insert_many(db_objs: typing.List[db.Model], db:SQLAlchemy) -> typing.NoReturn:
    '''
    inserts list of objects into db
    '''
    try:
        db.session.add_all([db_obj for db_obj in db_objs if type(db_obj) == db.Model])
        db.session.commit()
    except Exception as e:
        logging.exception(e, exc_info=True)


def select_all(obj_class: typing.Type[db.Model], db:SQLAlchemy):
    '''
    return all items in table defined by object class
    e.g items = select_all(Item, db)
    '''
    return db.session.query(obj_class).all()


def select_by_id(obj_class: typing.Type[db.Model], id: int, db:SQLAlchemy):
    '''
    return all items in table defined by object class and id
    e.g items = select_all(Item, 5, db)
    '''
    return db.session.query(obj_class).get(id)


def check_exists(obj: db.Model, db: SQLAlchemy) -> bool:
    '''
    check if obj exists in db
    '''
    obj_class = obj.__class__
    return db.session.query(obj_class.query.filter(obj_class == obj))











# PARSE TOOLTIPS (affix), add affix types, add affixes, add settings, make web-interface