from collections import defaultdict

from decimal import Decimal

from filter_app.app import db
from filter_app.dbhelper import select_all
from filter_app.gsheets.sheets_helper import write_sheet_data, append_sheet_data
from filter_app.models import Item, Category, Price, League
from sqlalchemy.sql import func


def _form_list_data(cat):
    """
    Selects item prices and dates from database
    """
    league_start =[l.start for l in db.session.query(League).all()
                   if l.is_current() and (not l.is_hardcore()) and l.main]
    if len(league_start)>0:
        league_start = league_start[0]
        dates = [str(p) for (p,) in db.session.query(func.date(Price.date))
            .filter(func.date(Price.date)>=league_start)  # only current league on the spreadsheet list
            .distinct()
            .order_by(func.date(Price.date))]
        items = db.session.query(Item).filter(Item.category_id == cat.id).order_by(Item.name)
        values = [["Date/Name"] + dates]  # first row -- table dates
        for i in items:
            fname = i.name + ", " + i.note  # first column -- item names
            row = [fname]
            prices_dates = [str(p.date.date()) for p in i.prices]  # all existing dates for current item
            for date in dates:
                if date in prices_dates:
                    item_prices = [Decimal(p.price) for p in i.prices if str(p.date.date()) == date]
                    temp = str(round(sum(item_prices)/Decimal(len(item_prices)), 2))
                    if temp:
                        row.append(temp)
                else:
                    row.append('n/a')
            values.append(row)
    return values


def write_prices():
    """
    Writes prices to the spreadsheet
    """
    spreadsheet_id = '1Z1A03eGihrpevvZtNvcCGfKpqyQMxqB8pAPj8gp81Ic' # extract from spreadsheet url
    for cat in select_all(Category):
        values = _form_list_data(cat)
        range_name = '%s!1:%s' % (cat.name, len(values))
        write_sheet_data(spreadsheet_id, range_name, values)


def append_prices():
    """
    Appends prices to the spreadsheet
    """
    spreadsheet_id = '1Z1A03eGihrpevvZtNvcCGfKpqyQMxqB8pAPj8gp81Ic' # extract from spreadsheet url
    for cat in select_all(Category, db):
        values = _form_list_data(cat)
        range_name = '%s!M1:M%s' % (cat.name, len(values)) # :TODO: need another range
        append_sheet_data(spreadsheet_id, range_name, values)

if __name__ == "__main__":
    write_prices()
