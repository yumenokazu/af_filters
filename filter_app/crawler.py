import logging
import time
import typing

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

'''
crawler module provides functions for getting source code of pages
'''


def request_url(link, web_driver):
    """
    returns source code of link requested
    """
    web_driver.get(link)
    #WebDriverWait(web_driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    WebDriverWait(web_driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table")))
    web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    logger = logging.getLogger('filter_app')
    try:
        web_driver.find_element_by_class_name("show-more").click()
        logger.info('show_more clicked')
    except NoSuchElementException:
        logger.warning('no show_more button')
    WebDriverWait(web_driver, 5)
    return web_driver.page_source


def request_with_tooltip(link, web_driver) -> typing.List[str]:
    '''
    returns list of source codes of items with tooltips
    '''
    web_driver.set_window_size(1124, 850)
    web_driver.get(link)

    web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    logger = logging.getLogger('filter_app')
    try:
        web_driver.find_element_by_class_name("show-more").click()
        logger.info('show_more clicked')
    except NoSuchElementException:
        logger.warning('no show_more button')
    WebDriverWait(web_driver, 5)
    trs_count = len(web_driver.find_elements_by_css_selector("tr"))
    page_sources = []

    for x in range(1, trs_count):
        sel = "tbody tr:nth-child(%s) img" % x
        e = web_driver.find_element_by_css_selector(sel)
        web_driver.execute_script("arguments[0].scrollIntoView(false);", e) # :TODO: изначально передавался не общий драйвер, потестировать снова scrollintoview + once_scrolled
        print(e.location_once_scrolled_into_view)
        e.click()
        time.sleep(1)
        page_sources.append(web_driver.page_source)
    return page_sources


def create_driver(driver_type: str) -> 'WebDriver':
    """
    creates and returns web_driver of specified type
    :param driver_type: 'JS' for PhantomJS, 'FF' for Firefox
    :return: selenium.webdriver.firefox.webdriver.WebDriver
    """
    if driver_type == 'JS':
        return webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])  # :TODO: Why phantom js not scrolling
    elif driver_type == "FF":
        binary = FirefoxBinary('C:\\Software\\ff\\firefox.exe') # :TODO: move path to config file
        return webdriver.Firefox(firefox_binary=binary)

