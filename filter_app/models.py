import datetime

import re

from sqlalchemy import CheckConstraint

from filter_app.app import db


# items with prices
class Item(db.Model):
    __tablename__ = 'item'

    def __init__(self, name, base, item_type, chaos):
        self.name = name  # 0st td, 1st span, 2nd span inside
        self.base = base  # 0st td, 1st span, 3rd span inside
        self.item_type = item_type  # 1nd td
        # self.exalt = exalt  # 4th td 1st span
        non_decimal = re.compile(r'[^\d.]+')
        self.chaos = non_decimal.sub('', chaos)  # 4th td 2nd span
        self.dynamic = non_decimal.sub('', chaos)

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    base = db.Column(db.String)
    item_type = db.Column(db.String)
    chaos = db.Column(db.Float)
    dynamic = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id')) # n:1 item:category, access .category

    affixes = db.relationship('Affix', backref='item')  # one item can have many affixes

    def __repr__(self):
        return "Item(name=%s, base=%s, type=%s, chaos=%s)" % (self.name, self.base, self.item_type, self.chaos)


# categories of items
class Category(db.Model):
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

    def __repr__(self):
        return "<Category(id='%s', name='%s', link='%s', quantity='%s', class_name='%s')" % (
            self.id, self.name, self.link, self.quantity, self.class_name)


# table with all affix types
class AffixType(db.Model):
    __tablename__ = 'affix_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  # affix name
    filter_name = db.Column(db.String) # affix abbr as in filter file
    is_percent = db.Column(db.Boolean)  # true if affix is in percents, false if raw value
    top = db.Column(db.String(3), CheckConstraint('top.in_(["max", "min"])', name = 'check_top'))  # minimize or maximize
    affixes = db.relationship('Affix', backref='affix_type')  # one affix type can have many affixes


# affixes with min and max values of each item
class Affix(db.Model):
    __tablename__ = 'affix'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))  # use .item to access associated object of class Item
    affix_id = db.Column(db.Integer, db.ForeignKey("affix_type.id"))  # use .affix_type property to access AffixType obj
    affix_min = db.Column(db.Integer)  # min affix value
    affix_max = db.Column(db.Integer)  # max affix value


# default settings for chaos and percentage, first priority
class GeneralSettings(db.Model):
    __tablename__ = 'general_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    affix_pct = db.Column(db.Integer)  # default value for all affixes
    chaos_threshold = db.Column(db.Integer) # threshold for price, check lower-priced items


# stores fixed percentage for item's affix value, second priority
class AffixSettings(db.Model):
    __tablename__ = 'affix_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    affix_id = db.Column(db.Integer, db.ForeignKey('affix.id'))
    affix_pct = db.Column(db.Integer)  # fixed value for this affix


# stores permutational settings for item's affixes,
# number of rows per item should be eq or less than (len(item.affixes) - fixed item's affixes)
# only one row per item -- works like default affix_pct overwritten
# two and more rows per item -- results in all combinations of values for affixes with non-fixed values
class ItemSettings(db.Model):
    __tablename__ = 'item_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id')) # item
    affix_pct = db.Column(db.String)   # affix pcts for item, comma-separated or JSON










