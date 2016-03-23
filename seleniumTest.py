"""
    Script to search through Gateway website, log path, and manipulate every
    setting. Pages are generally seen as either something to navigate or
    something to manipulate settings.
"""
import time
from datetime import datetime
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
# from selenium.webdriver.common.by import By
import logging

LOCATION = []

logging.basicConfig(filename='myLog.log',level=logging.INFO)
logging.info('New test started at ' +
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def logit(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        logging.info(func.__name__ + ' was called.')
        return func(*args, **kwargs)
    return with_logging


def init_driver():
    """ Create driver object for Selenium bindings.
        :return: webdriver object
    """
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)  # ensure AJAX items have loaded
    return driver


def login(driver):
    """ Go to website and log in.
    :param driver: webdriver object
    """
    driver.get('http://10.0.222.26:8080/Account/Login')
    assert 'Horizon Retail Solutions' in driver.title
    elem = driver.find_element_by_name('Username')
    elem.send_keys('username')
    elem = driver.find_element_by_name('Password')
    elem.send_keys('password')
    elem.send_keys(Keys.RETURN)
    assert 'No results found.' not in driver.page_source


@logit
def navigate(driver):
    """ Drill down through menu items. When out of menu buttons, call function
        to manipulate settings. Within settings there may be more main menu
        type buttons ==> call navigate again.
        :param driver: webdriver object
    """
    global LOCATION  # keep track of overall location
    LOCATION.append(get_heading(driver))
    logging.info('>>'.join(LOCATION))
    
    buttons = driver.find_elements_by_css_selector(
        'a.btn.btn-primary.btn-lg.btn-block')
    for button in buttons:
        button.click()
        navigate(driver)
    else:
        manipulate(driver)
        navigate(driver)
        
    del LOCATION[-1]


@logit
def manipulate(driver):
    """ Analyze page and manipulate settings accordingly.
        :param driver: webdriver object
    """
    rows = get_rows(driver)
    for row in rows:
        print(row)
		
    nav_dropdown(driver)


@logit
def nav_dropdown(driver):
    """ Drill down through dropdown menu.
        :param driver: webdriver object
    """
    select = Select(driver.find_element_by_id('SelectedCategoryID'))
    dropdown_list = select.options
    for option in dropdown_list[1:]:
        print(option.text)
        option.click()
        submit = driver.find_element_by_xpath(
            '//input[contains(@value,"Filter")]')
        submit.click()
        nav_settings(driver)


@logit
def nav_settings(driver):
    """ (same as manip_settings but is inside nav_dropdown
        so that it doesn't get called all over again)
        :param driver: webdriver object
    """
    pass


@logit
def manip_settings(driver):
    """ Iterate through rows and manipulate each setting.
        :param driver: webdriver object
    """
    table = driver.find_elements_by_xpath('//table[@class="table"]/tbody/tr')
    for i, row in enumerate(table[1:]):
        cols = table.find_elements_by_css_selector('td')
        print(cols[0])
        print(cols[1])
        print(cols[2])


def get_heading(driver):
    """ Find and print heading of page just inside <div class=panel-heading>.
        (this may be h1-h4 tags, but usually h2)
        :param driver: webdriver object
        :return: :class: `string`
    """
    heading = driver.find_element_by_xpath('//div[@class="panel-heading"]/*')
    return heading.text


def get_rows(driver):
    """ Receive a list of row objects from a table and 
	return a list of rows (name, def_value, *links)
        :param driver: webdriver object
    """
    rows = []
    table_rows = driver.find_elements_by_css_selector('tr')
    headers = table_rows[0].find_elements_by_css_selector('td')
    header = [i for i in headers]
    for row in table_rows[1:]:
        new_row = []
        cols = row.find_elements_by_css_selector('td')
        row_obj = RowSetting(cols[0].text, cols[1].text)
        buttons = cols[-1].find_elements_by_css_selector('a')
        for button in buttons:
            row_obj.add_btns(button.get_attribute('href'))
        rows.append(row_obj)
    return rows


class RowSetting:
    """ Creates an object out of a row on a settings page.
        Takes a name, default value, (possible other values), and
        a list of buttons.

        input: (row from a table)
	atrib: name, default value, and list of buttons
    """
    def __init__(self, name, def_value):
        self.name = name
        self.def_value = def_value
        self.btns = []

    def add_btns(self, btn):
        """ Input: tupel of button name and its link. """
        self.btns.append(btn)


if __name__ == '__main__':
    my_driver = init_driver()
    login(my_driver)
    navigate(my_driver)
    time.sleep(5)
    # driver.quit()  # All Done!
    print('Success')
    logging.info('Test ended at ' +
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
