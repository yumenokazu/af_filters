from collections import defaultdict

from filter_app.app import db
from filter_app.dbhelper import select_all
from filter_app.gsheets.sheets_helper import write_sheet_data, append_sheet_data
from filter_app.models import Item, Category, Price
from sqlalchemy.sql import func


def _form_list_data(cat):
    """
    Selects item prices and dates from database
    """
    dates = [str(p) for (p,) in db.session.query(func.date(Price.date).distinct()).order_by(func.date(Price.date))]
    items = db.session.query(Item).filter(Item.category_id == cat.id).order_by(Item.name)
    values = [["Date/Name"] + dates]  # first row -- table dates
    for i in items:
        fname = i.name + ", " + i.note
        row = [fname]
        prices_dates = [str(p.date.date()) for p in i.prices]
        for date in dates:
            if date in prices_dates:
                temp = [str(p.price) for p in i.prices if str(p.date.date()) == date]
                if temp:
                    row.append(temp[0])
            else:
                row.append('n/a')
        values.append(row)
    print(values)
    return values


def write_prices():
    """
    Writes prices to the spreadsheet
    """
    spreadsheet_id = '1Z1A03eGihrpevvZtNvcCGfKpqyQMxqB8pAPj8gp81Ic' # extract from spreadsheet url
    for cat in select_all(Category, db):
        values = _form_list_data(cat)
        range_name = '%s!1:%s' % (cat.name,len(values))
        write_sheet_data(spreadsheet_id, range_name, values)


def append_prices():
    """
    Appends prices to the spreadsheet
    """
    spreadsheet_id = '1Z1A03eGihrpevvZtNvcCGfKpqyQMxqB8pAPj8gp81Ic' # extract from spreadsheet url
    for cat in select_all(Category, db):
        values = _form_list_data(cat)
        range_name = '%s!M1:M%s' % (cat.name,len(values)) # :TODO: need another range
        append_sheet_data(spreadsheet_id, range_name, values)

if __name__ == "__main__":
    write_prices()
