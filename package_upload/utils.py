from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from logger_mod import Logger

class Utils(object):
    def wait_by_xpath(self, dr, x, t=125):
        """
        Wait for the elemnt to be rendered in the DOM
        :param dr: The browser's object
        :param x: expression to locate the element in the DOM
        :param t: time to wait until the element loads
        :return: the element once accessible.
        """
        Logger.logger.debug('Waiting for {0} to be rendered.'.format(x))
        element = WebDriverWait(dr, t).until(
            EC.presence_of_element_located((By.XPATH, x))
        )
        return element

    def wait_by_css(self, dr, x, t=125):
        """
        Wait for the elemnt to be rendered in the DOM
        :param dr: The browser's object
        :param x: expression to locate the element in the DOM
        :param t: time to wait until the element loads
        :return: the element once accessible.
        """
        Logger.logger.debug('Waiting for {0} to be rendered.'.format(x))
        element = WebDriverWait(dr, t).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, x))
        )
        return element

    def wait_by_css_mulitple_elems(self, dr, x, t=15):
        """
        Wait for the elemnt to be rendered in the DOM
        :param dr: The browser's object
        :param x: expression to locate the element in the DOM
        :param t: time to wait until the element loads
        :return: the element once accessible.
        """
        Logger.logger.debug('Waiting for {0} to be rendered.'.format(x))
        elements = WebDriverWait(dr, t).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, x))
        )
        return elements