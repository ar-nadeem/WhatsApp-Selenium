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

        super()._BaseWhatsapp__wait_by_type(self.DomPathsDict["searchBox"]["type"], self.DomPathsDict["searchBox"]["value"])
        self.browser.find_element(
            getattr(By, self.DomPathsDict["searchBox"]["type"]), self.DomPathsDict["searchBox"]["value"]).send_keys(query)
        
        super()._BaseWhatsapp__wait_by_type(self.DomPathsDict["searchResults"]["type"], self.DomPathsDict["searchResults"]["value"])

        time.sleep(0.25)
        return self.browser.find_element(
            getattr(By, self.DomPathsDict["searchResults"]["type"]), self.DomPathsDict["searchResults"]["value"])
    
    def __openChat(self, query):
        """Open a chat by searching for it"""
        ActionChains(self.browser).move_to_element(
            self.__search(query)).click().click().perform()
    
    def __getChatName(self):
        """Get the name of the current chat"""
        return self.browser.find_element(getattr(By, self.DomPathsDict["currentChatName"]["type"]), self.DomPathsDict["currentChatName"]["value"]).text
    
    def __getChatNameGroup(self):
        """Get the name of the current chat"""
        return self.browser.find_element(getattr(By, self.DomPathsDict["currentChatNameGroup"]["type"]), self.DomPathsDict["currentChatNameGroup"]["value"]).text
    
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
    
    def getMessages(self, chatName, all=False, scroll=None, manualSync=False):
        """Get messages from a chat"""
        
        self.__openChat(chatName)
        
        self._BaseWhatsapp__wait_by_type(self.DomPathsDict["chatBody"]["type"], self.DomPathsDict["chatBody"]["value"])

        chatBody = self.browser.find_element(getattr(By, self.DomPathsDict["chatBody"]["type"]), self.DomPathsDict["chatBody"]["value"])
        
        chatBody.click()

        try:
            channelName = self.__getChatNameGroup()
            channelType = "GC"
        except:
            channelName = self.__getChatName()
            channelType = "DM"

        
        if manualSync:
            print("Please sync manually | Press Enter to continue")
            input()
        else:
            
            if scroll:
                self._BaseWhatsapp__scroll(scroll,chatBody)
                
            if all:
                self._BaseWhatsapp__scrollToView(self.DomPathsDict["chatBody"]["type"], self.DomPathsDict["chatBody"]["value"])
                
        super()._BaseWhatsapp__wait_by_type(self.DomPathsDict["message"]["type"], self.DomPathsDict["message"]["value"])
        

        messages = self.browser.find_elements(getattr(By, self.DomPathsDict["message"]["type"]), self.DomPathsDict["message"]["value"])
        
        print (len(messages))
        fetchedMessages = []
        for message in messages:
            msg = self.__parseMessage(message, channelType)
            fetchedMessages.append(msg)
            print(msg)
            print("------------------")
        
        self.__saveToCSV(fetchedMessages, channelName)
    
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
    
    def __parseMessage(self, message, channelType):
        """Parse a message element to extract its details"""

        # Common
        try:
            date = message.find_element(
                getattr(By, self.DomPathsDict["messageDate"]["type"]), self.DomPathsDict["messageDate"]["value"]).text
        except:
            date = "NONE"

        try:
            msg = message.find_element(
                getattr(By, self.DomPathsDict["messageText"]["type"]), self.DomPathsDict["messageText"]["value"]).text
        except:
            msg = "MEDIA"

        try:
            repliedMsg = message.find_element(
                getattr(By, self.DomPathsDict["repliedMessage"]["type"]), self.DomPathsDict["repliedMessage"]["value"]).text
        except:
            repliedMsg = "NONE"


        # Specialize for DMs
        if channelType == "DM":
            try: 
                if "message-out" in message.get_attribute("class"):
                    msgSender = "You"
                else:
                    msgSender = self.__getChatName()
            except: # Error
                msgSender = "NONE"

            try:
                qoutedMessageElement = message.find_element(
                    getattr(By, self.DomPathsDict["quotedMessage"]["type"]), self.DomPathsDict["quotedMessage"]["value"])
                try:
                    repliedTo = qoutedMessageElement.find_element(
                        getattr(By, self.DomPathsDict["repliedToYou"]["type"]), self.DomPathsDict["repliedToYou"]["value"]).text
                except:
                    repliedTo = qoutedMessageElement.find_element(
                        getattr(By, self.DomPathsDict["repliedToOtherDM"]["type"]), self.DomPathsDict["repliedToOtherDM"]["value"]).text
            except:
                repliedTo = "NONE"
        


        # Specialize for Groups
        elif channelType == "GC":
            try: # For Group chats
                if "message-in" in message.get_attribute("class"):
                    msgSender = message.find_element(
                        getattr(By, self.DomPathsDict["messageSenderGroup"]["type"]), self.DomPathsDict["messageSenderGroup"]["value"]).text
                else:
                    msgSender = "You"
            except: # Error
                try:
                    msgSender = message.find_elements(
                        getattr(By, self.DomPathsDict["messageSenderGroupUnknownNumber"]["type"]), self.DomPathsDict["messageSenderGroupUnknownNumber"]["value"])[0].text
                except:
                    msgSender = "NONE"

            try:
                qoutedMessageElement = message.find_element(
                            getattr(By, self.DomPathsDict["quotedMessage"]["type"]), self.DomPathsDict["quotedMessage"]["value"])
                
                repliedTo = qoutedMessageElement.find_element(
                            getattr(By, self.DomPathsDict["repliedToGroup"]["type"]), self.DomPathsDict["repliedToGroup"]["value"]).text
            except:
                repliedTo = "NONE"
        
        


        
        return (date, msgSender, msg, repliedTo, repliedMsg) 
        # try:
        #     msg = message.find_element(
        #         By.CLASS_NAME, "_21Ahp").text
        # except:
        #     msg = "MEDIA"
            
        # try:  # For all chat
        #     # Check for reply
        #     repliedMsg = message.find_element(
        #         By.CLASS_NAME, "quoted-mention._11JPr").text
        #     # If didnt crash, means there is reply
        #     # Check for reply to for Other
        #     try:
        #         repliedTo = message.find_elements(
        #             # Any Reply to Other Person
        #             By.CLASS_NAME, "_3FuDI._11JPr")[-1].text
        #         # Check if you exists somehwere
        #         for z in message.find_elements(By.CLASS_NAME, "_11JPr"):
        #             if "You" in z.text:
        #                 repliedTo = "You"
        #     except:  # Wildcard reply to me
        #         repliedTo = "You"  # Reply to me
                
        # except:  # There is not a reply
        #     repliedTo = "NONE"
        #     repliedMsg = "NONE"
            
        # try:
        #     date = message.find_elements(
        #         By.CLASS_NAME, "l7jjieqr.fewfhwl7")[-1].text
        # except:
        #     date = "NONE"
            
        # # Try to get sender name if none means private chat
        # try:
        #     # Other person name in group chat
        #     msgSender = message.find_element(
        #         By.CLASS_NAME, "_3IzYj._6rIWC.p357zi0d").text
        # except:  # For private chat
        #     if "message-out" in message.get_attribute("class"):
        #         msgSender = "You"  # My name in private chat and group chat
        #     else:
        #         # Other person name in Private chat and group chat where they spam messages one after other
        #         try:
        #             data_plain_t = message.find_elements(
        #                 By.CLASS_NAME, "copyable-text")[0].get_attribute('data-pre-plain-text')
        #             msgSender = data_plain_t[data_plain_t.find(
        #                 "] ")+2:-2]  # Parse name from data
        #         except:
        #             msgSender = self.__getChatName()
                    
        # # Different wordarounds | Should be solved
        # if msg == "":
        #     msg = "Emoji"
        # if repliedMsg == "":
        #     repliedMsg = "Emoji"
        # if len(repliedMsg) == 4 and repliedMsg[1] == ":":
        #     repliedMsg = "VOICE NOTE"
        # return (date, msgSender, msg, repliedTo, repliedMsg) 