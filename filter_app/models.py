from datetime import datetime
from decimal import Decimal
import re
from typing import List, Tuple

from sqlalchemy import CheckConstraint, exists, and_, func, extract
from filter_app.app import db


class Base(db.Model):
    __abstract__ = True

    def exists(self):
        raise NotImplementedError

    @staticmethod
    def natural_pk():
        raise NotImplementedError


# items with prices
class Item(Base):
    __tablename__ = 'item'

    def __init__(self, name, base, item_type, chaos, note, fated = None):
        self.name = name  # 0st td, 1st span, 2nd span inside
        self.base = base  # 0st td, 1st span, 3rd span inside
        self.item_type = item_type  # 1nd td
        # self.exalt = exalt  # 4th td 1st span
        non_decimal = re.compile(r'[^\d.]+')
        self.chaos = non_decimal.sub('', chaos)  # 4th td 2nd span
        self.note = note
        fated = False if (fated is None) else True # false by default

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)  # item name
    base = db.Column(db.String)  # workpiece required for item creation
    item_type = db.Column(db.String)  # item type
    chaos = db.Column(db.Float)  # cost in chaos
    note = db.Column(db.String)  # note to distinguish between items with same name
    fated = db.Column(db.Boolean)  # property to determine whether item is fated (true) or not (false)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # n:1 item:category, access .category

    affixes = db.relationship('Affix', backref='item')  # one item can have many affixes
    prices = db.relationship('Price', backref='item') # one item can have many prices

    def exists(self):
        return db.session.query(exists().where(and_(Item.name == self.name, Item.note == self.note))).scalar()

    @staticmethod
    def natural_pk():
        return ['name', 'note']

    def __repr__(self):
        return "<Item(name=%s, base=%s, type=%s, chaos=%s, note=%s)>" % (self.name, self.base,
                                                                       self.item_type, self.chaos, self.note)


# categories of items
class Category(Base):
    __tablename__ = 'category'

    def __init__(self, name, link, quantity, class_name):
        self.name = name
        self.link = link
        self.quantity = quantity
        self.class_name = class_name

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True)
    link = db.Column(db.String, unique=True, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    class_name = db.Column(db.String, nullable=True)

    items = db.relationship('Item',
                            backref='category')  # one category can have many items, backref for item.category access

    def exists(self):
        return db.session.query(exists().where(Category.name == self.name)).scalar()

    @staticmethod
    def natural_pk():
        return ['name']

    def __repr__(self):
        return "<Category(id='%s', name='%s', link='%s', quantity='%s', class_name='%s')>" % (
            self.id, self.name, self.link, self.quantity, self.class_name)


# table with all affix types
class AffixType(Base):
    __tablename__ = 'affix_type'

    def __init__(self, name, filter_name, top="max"):
        self.name = name
        self.filter_name = filter_name
        self.top = top

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)  # affix name
    filter_name = db.Column(db.String)  # affix abbr as in filter file
    top = db.Column(db.String(3), CheckConstraint('top.in_(["max", "min"])', name='check_top'))  # minimize or maximize
    affixes = db.relationship('Affix', backref='affix_type', lazy='joined')  # one affix type can have many affixes

    def exists(self):
        #return db.session.query(exists().where(AffixType.name == self.name)).scalar()
        pk = {k: getattr(self, k) for k in self.natural_pk()} # natural pk keys and values
        return db.session.query(AffixType.query.filter_by(**pk).exists()).scalar()

    @staticmethod
    def natural_pk():
        return ['name']

    def __repr__(self):
        return "<AffixType(id='%s', name='%s', filter_name='%s', top='%s')>" % (
            self.id, self.name, self.filter_name, self.top)


# affixes with min and max values of each item
class Affix(Base):
    __tablename__ = 'affix'

    def __init__(self, af_text, affix_min, affix_max):
        self.af_text = af_text
        self.affix_min = affix_min
        self.affix_max = affix_max

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)  # use .item to access associated object of class Item
    af_text = db.Column(db.String)  # full affix text
    affix_id = db.Column(db.Integer, db.ForeignKey("affix_type.id"), nullable=False)  # use .affix_type property to access AffixType obj
    affix_min = db.Column(db.Numeric(10,5))  # min affix value
    affix_max = db.Column(db.Numeric(10,5))  # max affix value

    def exists(self):
        # :TODO: rewrite with dict
        return db.session.query(exists().where(and_(Affix.item_id == self.item_id,
                                                    Affix.af_text == self.af_text))).scalar()

    @staticmethod
    def natural_pk():
        return ['item_id', 'af_text']

    def af_text_shortener(self, repl=None) -> str:
        if repl is None:
            repl = ""
        letters = re.compile(r'[^a-zA-Z ]')  # everything except a-zA-z and space
        return letters.sub(repl, self.af_text).strip()

    def af_text_ranges(self) -> List[Tuple[str, str]]:
        return [tuple(map(Decimal, t)) for t in re.findall(r"\(([0-9.]+)-([0-9.]+)\)", self.af_text, re.IGNORECASE)]

    def __repr__(self):
        return "<Affix(id='%s', item_id='%s', af_text='%s', affix_id='%s', affix_min='%s', affix_max='%s')>" % (
            self.id, self.item_id, self.af_text, self.affix_id, self.affix_min, self.affix_max)


# default settings for chaos and percentage
class GeneralSettings(Base):
    __tablename__ = 'general_settings'

    default_threshold = 5
    default_pct_settings = 90

    def __init__(self, user_id: int, affix_pct: int, chaos_thr: int):
        self.user_id = user_id
        self.affix_pct = affix_pct
        self.chaos_threshold = chaos_thr

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    affix_pct = db.Column(db.Integer)  # default value for all affixes
    chaos_threshold = db.Column(db.Integer)  # threshold for price, check lower-priced items

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(user_id == user_id).one_or_none()

    def exists(self):
        pass

    @staticmethod
    def natural_pk():
        return ['user_id']

    def __repr__(self):
        return "<GeneralSettings(id='%s', user_id='%s', affix_pct='%s', chaos_threshold='%s')>" % (
            self.id, self.user_id, self.affix_pct, self.chaos_threshold)


# stores fixed percentage for item's affix value, second priority
class AffixSettings(Base):
    __tablename__ = 'affix_settings'

    def __init__(self, user_id, affix_id, affix_pct):
        self.user_id = user_id
        self.affix_id = affix_id
        self.affix_pct = affix_pct

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    affix_id = db.Column(db.Integer, db.ForeignKey('affix.id'))
    affix_pct = db.Column(db.Integer)  # fixed value for this affix

    def exists(self):
        pass

    @staticmethod
    def natural_pk():
        return ['user_id', 'affix_id']

    def __repr__(self):
        return "<AffixSettings(id='%s', user_id='%s', affix_id='%s', affix_pct='%s')>" % (
            self.id, self.user_id, self.affix_id, self.affix_pct)


# stores permutational settings for item's affixes,
# number of rows per item should be eq or less than (len(item.affixes) - fixed item's affixes)
# only one row per item -- works like default affix_pct overwritten
# two and more rows per item -- results in all combinations of values for affixes with non-fixed values
class ItemSettings(Base):
    __tablename__ = 'item_settings'

    def __init__(self, user_id, item_id, affix_pct):
        self.user_id = user_id
        self.item_id = item_id
        self.affix_pct = affix_pct

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))  # item
    is_checked = db.Column(db.Boolean) # true if item should be included in filter anyway
    affix_pct = db.Column(db.String)  # affix pcts for item, comma-separated or JSON

    def exists(self):
        pass

    @staticmethod
    def natural_pk():
        return ['user_id', 'item_id']

    def __repr__(self):
        return "<ItemSettings(id='%s', user_id='%s', item_id='%s', affix_pct='%s')>" % (
            self.id, self.user_id, self.item_id, self.affix_pct)


class User(Base):
    def __init__(self, nick):
        self.nick = nick

    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String)

    def exists(self):
        pass

    @staticmethod
    def natural_pk():
        return ['nick']

    def __repr__(self):
        return "<User(id='%s', nick='%s')>" % (
            self.id, self.nick)


# stores prices for items on each date
class Price(Base):
    __tablename__ = 'price'

    def __init__(self, item_id, price):
        self.item_id = item_id
        self.price = price

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"),
                        nullable=False)  # use .item to access associated object of class Item
    price = db.Column(db.Numeric(10,2))  # price in chaos
    date = db.Column(db.DateTime, server_default=func.now()) # server datetime on insert

    def exists(self):
        return db.session.query(exists().where(and_(Price.item_id == self.item_id,
                                                    func.DATE(Price.date) == datetime.now().date(),
                                                    extract('hour', Price.date) == datetime.now().hour))).scalar()

    @staticmethod
    def natural_pk():
        return ['item_id', 'date']

    def __repr__(self):
        return "<Price(id='%s', item_id='%s', price='%s', date='%s')>" % (
            self.id, self.item_id, self.price, self.date)


# stores leagues with start and end dates
class League(Base):

    def __init__(self, name, start, end, main):
        self.name=name
        self.start = start
        self.end = end
        self.main = main

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=True)
    main = db.Column(db.Boolean, nullable=False) # true if league, false if event

    def is_current(self):
        today = datetime.datetime.now().date()
        if (today > self.start.date()) and (today < self.end.date()):
            return True
        else:
            return False

    def is_hardcore(self):
        if self.name[-3:] == ' HC':
            return True
        else:
            return False

    def exists(self):
        return db.session.query(exists().where(League.name == self.name)).scalar()

    @staticmethod
    def natural_pk():
        return ['name']

    def __repr__(self):
        return "<League(id='%s', name='%s', start='%s', end='%s', main='%s')>" % (
            self.id, self.name, self.start, self.end, self.main)