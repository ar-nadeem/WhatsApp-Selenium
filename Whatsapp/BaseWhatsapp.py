from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

import json
import os
import sys
import time


class BaseWhatsapp:
    """Base class with common WhatsApp functionality"""
    
    def __init__(self, browser, xpath_dict):
        self.browser = browser
        self.XpathDict = xpath_dict
    
    def __wait(self, cName, timeout=60):
        """Wait for an element to be present on the page"""
        print("Waiting for element: {}".format(cName),
              " To load, timeout: {}".format(timeout), " seconds remaining")
        wait = WebDriverWait(self.browser, timeout)
        try:
            element = wait.until(
                EC.presence_of_element_located((By.ID, cName)))
        except:
            exit("Element not found")
        return element

    def __wait_by_type(self,type, value, timeout=60):
        """Wait for an element to be present on the page"""
        print("Waiting for element: {}".format(value),
              " To load, timeout: {}".format(timeout), " seconds remaining")
        wait = WebDriverWait(self.browser, timeout)
        try:
            element = wait.until(
                EC.presence_of_element_located((getattr(By, type), value)))
        except:
            exit("Element not found")
        return element
    
    def __moveMouseToElement(self, element):
        """Move mouse to an element"""
        ActionChains(self.browser).move_to_element(element).perform()

    def __mouseScroll(self, elem,count):
        self.__moveMouseToElement(elem)
        """Scroll mouse a specified number of times"""
        origin = ScrollOrigin.from_element(elem)
        ActionChains(self.browser).scroll_from_origin(origin, 0, count).perform()



    def __sendPageUP(self,elem, count):
        """Send PAGE_UP key a specified number of times"""
        for i in range(count):
            ActionChains(self.browser).send_keys(Keys.PAGE_UP).perform()
            time.sleep(0.1)
    
    def __scroll(self, count,elem):
        """Scroll up a specified number of times"""
        for i in range(count):
            self.__sendPageUP(elem,10)
            time.sleep(1.5)

    def __scrollDown(self, count):
        """Scroll down a specified number of times"""
        for i in range(count):
            ActionChains(self.browser).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.1)
    
    def __scrollToView(self, element_type,element):
        """Scroll until the page content doesn't change anymore"""
        elements = self.browser.find_elements(getattr(By, element_type), element_class)
        if not elements:
            return
            
        elements[0].click()
        while True:
            self.__sendPageUP(5)
            oldPage = self.browser.page_source
            if oldPage == self.browser.page_source:
                time.sleep(1)
                self.__sendPageUP(10)
                oldPage = self.browser.page_source
                if oldPage == self.browser.page_source:
                    time.sleep(3)
                    self.__sendPageUP(30)
                    oldPage = self.browser.page_source
                    if oldPage == self.browser.page_source:
                        time.sleep(10)
                        self.__sendPageUP(60)
                        oldPage = self.browser.page_source
                        if oldPage == self.browser.page_source:
                            break 