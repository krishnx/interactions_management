from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from logger_mod import Logger
from utils import Utils

import os
import argparse
import ConfigParser
from time import sleep

class UploadFile(object):
    def __init__(self, org_id, filename, content_type):
        self.org_id = org_id
        self.filename = filename
        self.content_type = content_type

    def login(self, browser, config=None):
        """
        Read from the username and password from config, login and return the browser's object.
        :param browser: browser's object
        :param config: configuration
        :return: browser's object
        """
        username = browser.find_element_by_name("login")
        password = browser.find_element_by_name("password")

        username.send_keys(config.get('LOGIN', 'email').strip())
        password.send_keys(config.get('LOGIN', 'password').strip())

        browser.find_element_by_xpath("//button[@type='submit']").click()

        ut = Utils()
        try:
            error_message = ut.wait_by_xpath(browser, "//div[@class='error-message']", 10)
            Logger.logger.error('Login failed')
            return False
        except:
            Logger.logger.debug('Logged in')

        return browser

    def upload(self, browser=None, config=None):
        """
        The complete Upload process of a file
        :param browser: browser's object
        :param config: configuration
        :return: bool
        """
        browser = self.login(browser, config)
        if not browser:
            return False

        ut = Utils()

        try:
            interactions_tab = ut.wait_by_xpath(browser,
                                    "//a[@href='?clients/organization/organization{0}/interactionsmanagement/all']".format(
                                        self.org_id))
            interactions_tab.click()
            Logger.logger.debug('On interactions page.')

            upload_icon = ut.wait_by_xpath(browser, "//a[@title='Upload File']")
            browser.execute_script("arguments[0].click();", upload_icon)
            Logger.logger.debug('Upload file dialogue box opened')

            if os.path.exists(os.path.join(self.filename)):
                browser.find_element_by_xpath("//input[@type='file']").send_keys(self.filename)
                Logger.logger.debug('Added the file to be uploaded.')
            else:
                Logger.logger.error('Failed to add the file to be uploaded.')
                raise Exception("File {0} does not exist.".format(self.filename))

            # Explicitly wait for 10 seconds, as the progress-indicator prohibits the further clicks.
            sleep(10)

            if self.content_type.lower() == 'readership':
                try:
                    browser.find_element_by_xpath("//label[@for='rdReadership']").click()
                except:
                    browser.find_element_by_css_selector(".ui-buttonset > label[for='rdReadership']").click()
            Logger.logger.debug("Selected content type as: {0}".format(self.content_type))

            # The template selection task TODO
            # try:
            #     browser.find_element_by_xpath('//input[@placeholder="Select an Upload Template"]').click()
            # except:
            #     Logger.logger.debug("oops!")

            # 3rd line getting timedout. :( TODO
            # try:
            #     browser.find_element_by_xpath('//input[@placeholder="Select an Investor"]').click()
            #     browser.find_element_by_xpath('//input[@class="input-v2 input-v2--long select-v2-ext__filter-input"]').send_keys("Krishna_CorpAxe_CSV_Buyside")
            #     browser.find_element_by_xpath("//div[contains(text(), 'Krishna_CorpAxe_CSV_Buyside')]").click()
            # except Exception as e:
            #     Logger.logger.debug(e)
            #     Logger.logger.debug("oops!")

            if self.filename.endswith("xml"):
                click_upload = ut.wait_by_xpath(browser, "//button[text()='Upload']")
            else:
                click_upload = ut.wait_by_xpath(browser, "//button[@class='button-v2 button-v2--main-color']")

            click_upload.click()
            Logger.logger.debug('Upload intiated.')

            okay = ut.wait_by_xpath(browser, "//button[text()='Okay']")
            browser.execute_script("arguments[0].click();", okay)

        except TimeoutException as t:
            Logger.logger.error("Timed out.")
            raise Exception(t)
        except Exception as e:
            Logger.logger.error("Upload failed.")
            Logger.logger.error(str(e))
            raise Exception(e)

        return True

if __name__ == "__main__":

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--org_id", type=int, help="The Sell side org id", required=True)
    parser.add_argument("-t", "--type", type=str, help="XML or Excel", required=True)
    parser.add_argument("-fn", "--filename", type=str, help="name of the file to be uploaded", required=True)
    parser.add_argument("-ct", "--content_type", type=str, help="Content type. Either Interaction or Readership.", required=True)
    args = parser.parse_args()
    
    if not (args.type.lower() == 'excel' or args.type.lower() == 'xml' or isinstance(args.org_id, int) or isinstance(args.org_id, str)):
        parser.print_help()
        raise Exception('invalid parameters.')

    Logger.logger.info('Starting the test case for <TITLE>')
    Logger.logger.debug('''with params:
    org_id: {0}
    type: {1}
    filename: {2}
    content_type: {3}'''.format(args.org_id, args.type, args.filename, args.content_type))

    base_url = config.get('BASE', 'base_url').strip()
    base_dir_path = config.get('BASE', 'base_dir_path').strip()
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(base_url + config.get('BASE', 'sellside_dashboard_url').format(args.org_id))

    uf = UploadFile(args.org_id, os.path.join(base_dir_path, args.filename), args.content_type)
    uf.upload(browser)