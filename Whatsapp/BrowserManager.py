from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os
import sys
import time
import threading

from .BaseWhatsapp import BaseWhatsapp


class BrowserManager(BaseWhatsapp):
    """Class for managing the browser and login functionality"""
    
    def __init__(self, browser, xpath_dict):
        super().__init__(browser, xpath_dict)
    
    def __addOption(self, option):
        """Add a Chrome option"""
        self.browser.options.add_argument(option)
    
    def login(self):
        """Login to WhatsApp Web"""
        self.browser.get('https://web.whatsapp.com')
        if not self.__isLogin():
            print("Please scan the QR code")
            print("After 3 sec if not already logged in - Screenshot of QR code will be saved in: {}".format(
                os.path.join(sys.path[0], "QRCode.png")))
            
            # Create a timer to save the QR code after 3 seconds
            qr_timer = threading.Timer(3.0, self.__saveQRCode)
            qr_timer.start()
            
            while not self.__isLogin():
                pass
                
            # Cancel the timer if login happens before 3 seconds
            qr_timer.cancel()
            
            print("Login successful")
            try:
                myElem = self.browser.find_element(
                    By.XPATH, "/html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[2]/div/button/div/div")
                ActionChains(self.browser).move_to_element(
                    myElem).click().perform()

                print("Clicked ok on new look")
            except:
                print("No new look popup seen, skipped")
        else:
            print("Already logged in")
    
    def __saveQRCode(self):
        """Save the QR code screenshot"""
        self.browser.save_screenshot(
            os.path.join(sys.path[0], "QRCode.png"))
    
    def __isLogin(self):
        """Check if the user is logged in"""
        try:
            # Landing Page (Login QR Code page)
            self.browser.find_element(By.CLASS_NAME, "landing-wrapper")
        except:
            try:
                # Logged in (Chat list)
                self.browser.find_element(By.CLASS_NAME, "two")
                return True
            except:
                return False
        return False
    
    def test(self):
        """Test the browser by navigating to Google"""
        self.browser.get('https://www.google.com')
        print(self.browser.title) 