import re
import os
from typing import Tuple, List, NoReturn
from filter_app.dbhelper import insert

from bs4 import BeautifulSoup

from filter_app.app import db, app
from filter_app.dbhelper import select_all
from filter_app import crawler
from filter_app.models import Item, Category, Affix, AffixType
from filter_app.definitions import ROOT_DIR


def _parse_link(cat: str, web_driver) -> NoReturn:
    '''
    parse link and create files for further parsing
    '''
    sources = crawler.request_with_tooltip(cat.link, web_driver)
    for index, item in enumerate(sources):
        if str(item).find("tooltip") == -1:
            print(index)
        file_path = os.path.relpath('files\\%s\\%s.txt' % (cat.name, index))
        f = open(file_path, 'w', encoding='utf-8')
        print(item, file=f)
        f.close()
    web_driver.quit()


def parse_files(cat: Category) -> Tuple[List[Tuple[Item, List[Affix]]], List[str]]:
    """
    parse html files and return items with tooltips
    """
    l = []
    s = []
    path = os.path.join(ROOT_DIR, 'files\\%s' % cat.name)  # get path to current category
    files = os.walk(path).__next__()
    file_count = len(files[2])  # count files in category folder
    for i in range(0, file_count):
        path = 'files\\%s\\%s.txt' % (cat.name, i)
        with open(path, 'r', encoding='utf-8') as f:
            page = f.read()  # page source with tooltip present
            item, affixes = _parse_page_with_tooltip(page, i)  # :TODO: check parsing for other categories
            item.category_id = cat.id
            item.dynamic = item.chaos
            l.append((item, affixes))
            # print(tooltip)
            for af in affixes:
                s.append(af.af_text)
    return (l, s)


def _parse_cols(cols)-> Item:
    col0spans = cols[0].find("span").find_all("span")
    name = col0spans[1].text
    base = cols[0].find("span", class_="faded-text").text[2:]
    item_type = cols[1].text
    chaos = cols[4].find("img", {"title": "Chaos Orb"}).previousSibling
    note = col0spans[2].text[2:]
    return Item(name, base, item_type, chaos, note)  # create Item object from parsed values


def parse_page(html: str) -> List[Item]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("tbody")
    rows = table.find_all('tr')
    items = []
    for row in rows:
        cols = row.find_all('td')
        item = _parse_cols(cols)
        items.append(item)
    return items


def _parse_page_with_tooltip(html: str, pos: int) -> Tuple[Item, List[Affix]]:
    """
    parse html page for a particular accessory defined by pos
    :param html: html page code, str
    :param pos: position in the table, int
    :return: Item and list of its affixes
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("tbody")
    rows = table.find_all('tr')
    cols = rows[pos].find_all('td')
    item = _parse_cols(cols)
    # print(pos)
    soup.find("div", class_="flavour-text").decompose()
    tooltip = soup.find_all("div", class_="tooltip-body")
    temp = soup.find("div", class_="tooltip-title").text

    def _parse_tooltip(tooltip, strings):
        for div in tooltip:
            if div.find_all("div", recursive=False) == []:
                if div.text != "":
                    if re.search("\(([0-9\.]+)-", div.text, re.IGNORECASE) is not None:  # only with range
                        strings.append(div.text)
            else:
                _parse_tooltip(div, strings)
        return strings

    divs = _parse_tooltip(tooltip, strings=[])
    af = []
    for div in divs:
        af_range = re.findall("([0-9\.]+)", div, re.IGNORECASE)
        af_min = 0
        af_max = 0
        if af_range:
            af_min = af_range[0]
            af_max = af_range[1]
        af.append(Affix(div,af_min,af_max))
    return (item, af)


def _parse_affixes(cat: Category) -> List[str]:
    """
    returns list of all distinct affixes with range (e. g. 10-25) from items in category
    """
    app.logger.info("Start parsing category: %s" % cat.name)
    data = parse_files(cat)

    affixes_with_dupes = data[1]
    affixes_no_dupes = []
    for index, entry in enumerate(affixes_with_dupes):
        affix = Affix(entry, None, None)
        if '-' in affix.af_text:
            entry = Affix.keep_letters("")  # replace everything matching letters pattern in entry with ''
            affixes_no_dupes.append(entry)  # fill list with range affixes
    affixes_no_dupes = list(set(affixes_no_dupes))
    s = sorted(affixes_no_dupes)
    return s


def parse_new():
    """
    get data in each category using web_driver, write data to files, read, parse & print results
    """
    cats = select_all(Category, db)  # get categories for parsing
    for cat in cats:
        print(cat.link)
        driver = crawler.create_driver('FF')
        _parse_link(cat, driver)  # write files


def parse_existing_af():
    """
    print all existing range affixes with no duplicates
    """
    cats = select_all(Category, db)  # get categories for parsing
    sorted_list = []
    for cat in cats:
        print(cat.link)
        sorted_list.extend(_parse_affixes(cat))
    for item in sorted(list(set(sorted_list))):
        print(item)


def parse_existing_files():
    cats = select_all(Category, db)  # get categories for parsing
    for cat in cats:
        print(len(parse_files(cat)[0]))  # read files and parse them



# logging.basicConfig(level=logging.DEBUG)

