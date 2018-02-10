import re
import os
from typing import Tuple, List, NoReturn

from bs4 import BeautifulSoup

from filter_app.app import db
from filter_app.dbhelper import select_all
from filter_app import crawler
from filter_app.models import Item, Category
from filter_app.definitions import ROOT_DIR


class AffixTemp:
    def __init__(self, full_affix, affix_name, is_percent, left_min, right_max):
        self.full_affix = full_affix
        self.affix_name = affix_name
        self.is_pct = is_percent
        self.left_min = left_min
        self.right_max = right_max


def parse_link(cat: str, web_driver) -> NoReturn:
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


def parse_files(cat: Category) -> Tuple[List[Tuple[Item, List[str]]], List[str]]:
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
            data = f.read()  # page source with tooltip present
            item, tooltip = _parse_accessories(data, i)  # :TODO: check parsing for other categories
            item.category_id = cat.id
            item.dynamic = item.chaos
            l.append((item, tooltip))
            # print(tooltip)
            for t in tooltip:
                s.append(t)
    return (l, s)


def _parse_accessories(html: str, pos: int) -> Tuple[Item, List[str]]:
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
    item = Item(name, base, item_type, chaos)
    soup.find("div", class_="flavour-text").decompose()
    tooltip = soup.find_all("div", class_="tooltip-body")
    temp = soup.find("div", class_="tooltip-title").text
    def _parse_tooltip(tooltip, strings):
        for div in tooltip:
            if div.find_all("div", recursive=False) == []:
                if div.text != "":
                    strings.append(div.text)
                    if str(div.text).lower().find("for each Enemy hit by your Spells".lower()) != -1:
                        print(tooltip)
                        print(item)
            else:
                _parse_tooltip(div, strings)
        return strings

    divs = _parse_tooltip(tooltip, strings=[])
    return (item, divs)


def _parse_affixes(cat: Category):
    """
    prints all distinct affixes with range (e. g. 10-25) from items in category
    """
    data = parse_files(cat)
    letters = re.compile(r'[^a-zA-Z ]')  # everything except a-zA-z and space
    affixes_with_dupes = data[1]
    affixes_no_dupes = []
    for index, entry in enumerate(affixes_with_dupes):
        if '-' in entry:
            entry = letters.sub('', entry).strip()  # replace everything matching letters pattern in entry with ''
            affixes_no_dupes.append(entry) # fill list with range affixes
    affixes_no_dupes = list(set(affixes_no_dupes))
    s = sorted(affixes_no_dupes)
    #for affix in s:
        #print(affix)
    return s


cats = select_all(Category, db)
# for cat in cats:
#     print(cat.link)
#     driver = crawler.create_driver('FF')
#     parse_link(cat, driver) # write files
# for cat in cats:
#     print(len(parse_files(cat)[0])) # read files and parse them
affixes = []
affixes_ = _parse_affixes(cats[0])
with open("F:\\affixes not full.txt") as f:
    for line in f:
        affixes.append(line.rstrip())
print(len(affixes)) # uaccessories_backup
print(len(affixes_)) # uaccessories
print(set(affixes_) - set(affixes))
print(set(affixes) - set(affixes_))
# PARSE TOOLTIPS (affix), add affix types, add affixes, add settings, make web-interface
