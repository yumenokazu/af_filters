import typing
import logging
from filter_app.app import db


def commit():
    """
    commits
    """
    # :TODO: everything's wrong here
    db.session.commit()


def insert(db_obj: db.Model) -> typing.NoReturn:
    '''
    inserts single db_obj into db
    '''
    if issubclass(type(db_obj), db.Model):
        try:
            if not db_obj.exists():
                db.session.add(db_obj)
                db.session.commit()
        except Exception as e:
            logging.exception(e, exc_info=True)


def insert_many(db_objs: typing.List[db.Model]) -> typing.NoReturn:
    '''
    inserts list of objects into db
    '''
    try:
        db.session.add_all([db_obj for db_obj in db_objs if type(db_obj) == db.Model])
        db.session.commit()
    except Exception as e:
        logging.exception(e, exc_info=True)


def update(db_obj: db.Model, fields: typing.Dict) -> typing.NoReturn:
    """
    updates attributes on existing db_obj
    :param db_obj:
    :param fields: dictionary of attribute names and respective values
    """
    try:
        for k, v in fields.items():
            setattr(db_obj, k, v)
        db.session.commit()
    except Exception as e:
        logging.exception(e, exc_info=True)


def select_all(obj_class: typing.Type[db.Model]):
    '''
    returns all items in table defined by object class
    e.g items = select_all(Item, db)
    '''
    return db.session.query(obj_class).all()


def select_by_id(obj_class: typing.Type[db.Model], id: int):
    '''
    returns all items in table defined by object class and id
    e.g items = select_all(Item, 5, db)
    '''
    return db.session.query(obj_class).get(id)


def select_by_fields(obj_class: typing.Type[db.Model], fields: typing.Dict):
    """
    returns all items filtered by {field: value} in fields dictionary in table defined by object class
    :param obj_class: mapped class
    :param fields: dictionary with fields and their values
    :param db: object for querying database
    :return: list of objects of obj_class or None
    """
    if fields:
        return db.session.query(obj_class).filter_by(**fields)
    else:
        return None




