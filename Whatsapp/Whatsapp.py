from selenium import webdriver
import json
import os
import sys

from .MessageHandler import MessageHandler
from .BrowserManager import BrowserManager


print("User data will be saved in: {}".format(
    os.path.join(sys.path[0], "UserData. Keep this folder private")))
print("xpaths.json file should be in the same directory as this file")
print("If you want to change the xpaths, please edit the xpaths.json file. Then please create a Github Pull Request.")


class Whatsapp:
    """Main WhatsApp automation class that combines browser management and message handling"""
    
    def __init__(self, executable_path=None, silent=False, headless=False):
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dom_paths = os.path.join(current_dir, "dom_paths.json")
        
        with open(dom_paths, "r") as file:
            self.DomPathsDict = json.load(file)

        self.options = webdriver.ChromeOptions()
        if silent:
            self.options.add_argument("--log-level=3")
        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
            self.options.add_argument("--window-size=1920,1080")
            self.options.add_argument("--no-sandbox")

        self.options.add_argument(
            "user-data-dir={}".format(os.path.join(sys.path[0], "UserData")))

        if executable_path:
            self.browser = webdriver.Chrome(
                options=self.options, executable_path=executable_path)
        else:
            self.browser = webdriver.Chrome(options=self.options)
            
        # Initialize the specialized classes
        self.browser_manager = BrowserManager(self.browser, self.DomPathsDict)
        self.messages = MessageHandler(self.browser, self.DomPathsDict)
    
    # Delegate browser management methods
    def test(self):
        return self.browser_manager.test()
        
    def login(self):
        return self.browser_manager.login()
    
    # Delegate message handling methods
    def getChats(self):
        return self.messages.getChats()
        
    def getMessages(self, chatName, all=False, scroll=None, manualSync=False, element="_1AOLJ._1jHIY"):
        return self.messages.getMessages(chatName, all, scroll, manualSync, element)
        
    def getMessagesOutgoing(self, chatName, all=False, scroll=None, manualSync=False):
        return self.messages.getMessagesOutgoing(chatName, all, scroll, manualSync)
        
    def getMessagesIncomming(self, chatName, all=False, scroll=None, manualSync=False):
        return self.messages.getMessagesIncomming(chatName, all, scroll, manualSync)
        
    def hookIncomming(self, chatName, func):
        return self.messages.hookIncomming(chatName, func)
        
    def replyTo(self, element, msg):
        return self.messages.replyTo(element, msg)
        
    def sendMessage(self, msg):
        return self.messages.sendMessage(msg)

