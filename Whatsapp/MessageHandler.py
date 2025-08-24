from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import csv
import os
import sys
import time
from typing import List
import asyncio

from .BaseWhatsapp import BaseWhatsapp

class MessageHandler(BaseWhatsapp):
    """Class for handling WhatsApp messages"""
    
    def __init__(self, browser, DomPathsDict):
        super().__init__(browser, DomPathsDict)
        self.oldHookedMessage = None
        self.DomPathsDict = DomPathsDict

    
    def __saveToCSV(self, data, name):
        """Save message data to a CSV file"""
        fileName = name + ".csv"
        with open(fileName, 'w', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(("Date", "Sender", "Message",
                            "Replied To", "Replied Message"))
            writer.writerows(data)
    
    def __search(self, query):
        """Search for a chat or contact"""
        self.browser.find_element(
            By.CLASS_NAME, "copyable-text").send_keys(query)
        self.browser.save_screenshot(
            os.path.join(sys.path[0], "Searched !.png"))
        time.sleep(0.25)
        return self.browser.find_element(By.CLASS_NAME, "matched-text")
    
    def __openChat(self, query):
        """Open a chat by searching for it"""
        ActionChains(self.browser).move_to_element(
            self.__search(query)).click().click().perform()
    
    def __getChatName(self):
        """Get the name of the current chat"""
        return self.browser.find_element(By.CLASS_NAME, "_3W2ap").text
    
    def getChats(self) -> List[str]:
        """Get a list of all chats"""
        self._BaseWhatsapp__wait(self.DomPathsDict["chatPannel"]["value"])


        # Scroll until old Names = new Names
        chats = []
        # Group Names
        oldNames = [el.text for el in self.browser.find_elements(
            getattr(By, self.DomPathsDict["chatNames_Group"]["type"].upper()), 
            self.DomPathsDict["chatNames_Group"]["value"])]
        # Single Names
        oldNames += [el.text for el in self.browser.find_elements(
            getattr(By, self.DomPathsDict["chatNames_Singluar"]["type"].upper()), 
            self.DomPathsDict["chatNames_Singluar"]["value"])]
        
        newNames =[]
        for name in oldNames:
            chats.append(name)
        
        while True:
            scrollFrom = self.browser.find_elements(
            getattr(By, self.DomPathsDict["chatPannelElement"]["type"].upper()),
            self.DomPathsDict["chatPannelElement"]["value"])[-1]
            
            super()._BaseWhatsapp__mouseScroll(scrollFrom,500)
            time.sleep(0.1)

            # Get New Names
            # Group Names
            newNames = [el.text for el in self.browser.find_elements(
            getattr(By, self.DomPathsDict["chatNames_Group"]["type"].upper()), 
            self.DomPathsDict["chatNames_Group"]["value"])]
            # Single Names
            newNames += [el.text for el in self.browser.find_elements(
            getattr(By, self.DomPathsDict["chatNames_Singluar"]["type"].upper()), 
            self.DomPathsDict["chatNames_Singluar"]["value"])]

            if oldNames == newNames:
                break
            oldNames = newNames
            
            for name in newNames:
                chats.append(name)

        


        # Print only unique chat names
        uniqueChats = []
        for chat in chats:
            if (chat == ""):
                continue
            if chat not in uniqueChats:
                uniqueChats.append(chat)
                print(chat)
        return uniqueChats
    
    def getMessages(self, chatName, all=False, scroll=None, manualSync=False, element="_1AOLJ._1jHIY"):
        """Get messages from a chat"""
        self.__openChat(chatName)
        
        self._BaseWhatsapp__wait(element)
        
        self.browser.find_elements(By.CLASS_NAME, element)[0].click()
        
        if manualSync:
            print("Please sync manually | Press Enter to continue")
            input()
        else:
            if scroll:
                self._BaseWhatsapp__scroll(scroll, element)
                
            if all:
                self._BaseWhatsapp__scrollToView(element)
                
        time.sleep(3)
        messages = self.browser.find_elements(By.CLASS_NAME, element)
        
        fetchedMessages = []
        for message in messages:
            msg = self.__parseMessage(message)
            fetchedMessages.append(msg)
            print(msg)
            print("------------------")
            
        self.__saveToCSV(fetchedMessages, self.__getChatName())
    
    def getMessagesOutgoing(self, chatName, all=False, scroll=None, manualSync=False):
        """Get outgoing messages from a chat"""
        self.getMessages(chatName, all, scroll, manualSync, "message-out")
    
    def getMessagesIncomming(self, chatName, all=False, scroll=None, manualSync=False):
        """Get incoming messages from a chat"""
        self.getMessages(chatName, all, scroll, manualSync, "message-in")
    
    def hookIncomming(self, chatName, func):
        """Hook into incoming messages and call a function for each new message"""
        self.oldHookedMessage = None
        asyncio.run(self.__hookIncomming(chatName, func))
    
    async def __hookIncomming(self, chatName, func):
        """Internal method for hooking into incoming messages"""
        self.__openChat(chatName)
        time.sleep(0.1)
        self.browser.save_screenshot(os.path.join(sys.path[0], "Waiting.png"))
        self._BaseWhatsapp__wait("message-in")
        
        message = self.browser.find_elements(By.CLASS_NAME, "message-in")[-1]
        
        while True:
            while self.oldHookedMessage == message:
                await asyncio.sleep(0.1)
                message = self.browser.find_elements(
                    By.CLASS_NAME, "message-in")[-1]
                
            await asyncio.create_task(func(message, self.__parseMessage(message)))
            self.oldHookedMessage = message
    
    def replyTo(self, element, msg):
        """Reply to a specific message"""
        totalretries = 5
        dropDown = 'span[data-testid="down-context"][data-icon="down-context"]'
        
        # Try again and again. As new message cancels the all clicks.
        while True and totalretries > 0:
            try:
                # Click the message to make the drop down appear
                ActionChains(self.browser).move_to_element(
                    element.find_elements(By.CLASS_NAME, "l7jjieqr.fewfhwl7")[0]).click().perform()
                
                # Click Drowndown
                dropDown = self.browser.find_element(By.CSS_SELECTOR, dropDown)
                ActionChains(self.browser).move_to_element(
                    dropDown).click().perform()
                
                # Click Reply
                time.sleep(0.1)  # Wait for the reply button to appear
                
                self.browser.find_element(
                    By.CSS_SELECTOR, 'div[aria-label="Reply"]').click()
                
                # Send the message
                self.sendMessage(msg)
                break
            except:
                print("Failed ! Retrying... tries left: " + str(totalretries))
                time.sleep(0.25)
                totalretries -= 1
                pass
    
    def sendMessage(self, msg):
        """Send a message in the current chat"""
        # Click on message box
        myElem = self.browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]")
        ActionChains(self.browser).move_to_element(myElem).click().perform()
        ActionChains(self.browser).send_keys(msg).perform()
        # Click send button
        self.browser.find_element(
            By.XPATH, "/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]/div[2]/button").click()
    
    def __parseMessage(self, message):
        """Parse a message element to extract its details"""
        try:
            msg = message.find_element(
                By.CLASS_NAME, "_21Ahp").text
        except:
            msg = "MEDIA"
            
        try:  # For all chat
            # Check for reply
            repliedMsg = message.find_element(
                By.CLASS_NAME, "quoted-mention._11JPr").text
            # If didnt crash, means there is reply
            # Check for reply to for Other
            try:
                repliedTo = message.find_elements(
                    # Any Reply to Other Person
                    By.CLASS_NAME, "_3FuDI._11JPr")[-1].text
                # Check if you exists somehwere
                for z in message.find_elements(By.CLASS_NAME, "_11JPr"):
                    if "You" in z.text:
                        repliedTo = "You"
            except:  # Wildcard reply to me
                repliedTo = "You"  # Reply to me
                
        except:  # There is not a reply
            repliedTo = "NONE"
            repliedMsg = "NONE"
            
        try:
            date = message.find_elements(
                By.CLASS_NAME, "l7jjieqr.fewfhwl7")[-1].text
        except:
            date = "NONE"
            
        # Try to get sender name if none means private chat
        try:
            # Other person name in group chat
            msgSender = message.find_element(
                By.CLASS_NAME, "_3IzYj._6rIWC.p357zi0d").text
        except:  # For private chat
            if "message-out" in message.get_attribute("class"):
                msgSender = "You"  # My name in private chat and group chat
            else:
                # Other person name in Private chat and group chat where they spam messages one after other
                try:
                    data_plain_t = message.find_elements(
                        By.CLASS_NAME, "copyable-text")[0].get_attribute('data-pre-plain-text')
                    msgSender = data_plain_t[data_plain_t.find(
                        "] ")+2:-2]  # Parse name from data
                except:
                    msgSender = self.__getChatName()
                    
        # Different wordarounds | Should be solved
        if msg == "":
            msg = "Emoji"
        if repliedMsg == "":
            repliedMsg = "Emoji"
        if len(repliedMsg) == 4 and repliedMsg[1] == ":":
            repliedMsg = "VOICE NOTE"
        return (date, msgSender, msg, repliedTo, repliedMsg) 