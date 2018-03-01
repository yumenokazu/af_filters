import re
import os
from typing import Tuple, List, NoReturn

from bs4 import BeautifulSoup

from filter_app.app import db, app
from filter_app.dbhelper import select_all
from filter_app import crawler
from filter_app.models import Item, Category, Affix
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


def _parse_files(cat: Category) -> Tuple[List[Tuple[Item, List[Affix]]], List[str]]:
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
        with open(path) as f:
            page = f.read()  # page source with tooltip present
            item, affixes = _parse_page(page, i)  # :TODO: check parsing for other categories
            item.category_id = cat.id
            item.dynamic = item.chaos
            l.append((item, affixes))
            # print(tooltip)
            for af in affixes:
                s.append(af.af_text)
    return (l, s)


def _parse_page(html: str, pos: int) -> Tuple[Item, List[Affix]]:
    """
    parse html page for a particular accessory defined by pos
    :param html: html page code, str
    :param pos: position in the table, int
    :return: Item and list of its affixes
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("tbody")
    rows = table.find_all('tr')
    tds = rows[pos].find_all('td')
    # print(pos)
    td1spans = tds[0].find("span").find_all("span")
    fourth_span = tds[4].find("img", {"title": "Chaos Orb"})
    name = td1spans[1].text
    base = tds[0].find("span", class_="faded-text").text[2:]
    item_type = tds[1].text
    chaos = fourth_span.previousSibling
    item = Item(name, base, item_type, chaos)  # create Item object from parsed values
    item.note = td1spans[2].text[2:]
    soup.find("div", class_="flavour-text").decompose()
    tooltip = soup.find_all("div", class_="tooltip-body")
    temp = soup.find("div", class_="tooltip-title").text

    def _parse_tooltip(tooltip, strings):
        for div in tooltip:
            if div.find_all("div", recursive=False) == []:
                if div.text != "":
                    if re.search("([0-9\.]+)-", div.text, re.IGNORECASE) is not None:  # only with range
                        strings.append(div.text)
            else:
                _parse_tooltip(div, strings)
        return strings

    divs = _parse_tooltip(tooltip, strings=[])
    af = []
    for div in divs:
        print(div)
        af_range = re.findall("([0-9\.]+)", div, re.IGNORECASE)
        af_min = 0
        af_max = 0
        if af_range:
            print(af_range)
            af_min = af_range[0]
            af_max = af_range[1]
        af.append(Affix(div,af_min,af_max))
    return (item, af)


def _parse_affixes(cat: Category) -> List[str]:
    """
    returns list of all distinct affixes with range (e. g. 10-25) from items in category
    """
    app.logger.info("Start parsing category: %s" % cat.name)
    data = _parse_files(cat)
    letters = re.compile(r'[^a-zA-Z ]')  # everything except a-zA-z and space
    affixes_with_dupes = data[1]
    affixes_no_dupes = []
    for index, entry in enumerate(affixes_with_dupes):
        if '-' in entry:
            entry = letters.sub('', entry).strip()  # replace everything matching letters pattern in entry with ''
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
        print(len(_parse_files(cat)[0]))  # read files and parse them


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
        data = _parse_files(cat)  # read files and parse them
        for tuple_ in data[0]:
            print(tuple_[0])  # Item (ready to insert, need item_id to connect affix)
            for affix in tuple_[1]:  # list of tooltips of  current item
                print(affix)
                # :TODO: get affix type and update id
                tuple[0].affixes.append(affix)


parse_existing_files()
# logging.basicConfig(level=logging.DEBUG)
# add affix types, add affixes, add settings, make web-interface
# af count: ac 406, wea 529, arm 738
