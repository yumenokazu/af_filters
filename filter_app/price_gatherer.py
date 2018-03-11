from filter_app.app import db
from filter_app.crawler import request_url, create_driver
from filter_app.parser import parse_page
from filter_app.dbhelper import select_all, insert
from filter_app.models import Category, Price, Item
import logging


def gather_prices():
    """
    gather current prices for items in each category and insert gathered data into price table
    """
    driver = create_driver('FF') # create driver
    cats = select_all(Category, db)  # get links for parsing
    db_items = select_all(Item, db)  # get existing items
    prices = []
    for cat in cats:
        logging.debug("Category link: %s" % cat.link)
        source = request_url(cat.link, driver)
        items = parse_page(source)
        for item in items:
            for db_item in db_items:
                if (item.name == db_item.name) and (item.note == db_item.note):
                    price_obj = Price(db_item.id, item.chaos)
                    prices.append(price_obj)
    driver.quit()
    for price_obj in prices:
        insert(price_obj, db)