from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import csv
import os
import sys
import time

print("User data will be saved in: {}".format(
    os.path.join(sys.path[0], "UserData")))


class WhatsExtract:
    def __init__(self, executable_path=None, silent=False, headless=False):
        self.options = webdriver.ChromeOptions()
        if silent:
            self.__addOption("--log-level=3")
        if headless:
            self.__addOption("--headless")

        self.__addOption(
            "user-data-dir={}".format(os.path.join(sys.path[0], "UserData")))

        if executable_path:
            self.browser = webdriver.Chrome(
                options=self.options, executable_path=executable_path)
        else:
            self.browser = webdriver.Chrome(options=self.options)

    def test(self):
        self.browser.get('https://www.google.com')
        print(self.browser.title)

    def __addOption(self, option):
        self.options.add_argument(option)

    def login(self):
        self.browser.get('https://web.whatsapp.com')
        if not self.__isLogin():
            print("Please scan the QR code")
            while not self.__isLogin():
                pass
            print("Login successful")
        else:
            print("Already logged in")

    def getChats(self):
        self.__wait("two")
        chats = self.browser.find_elements(By.CLASS_NAME, "_11JPr")
        for chat in chats:
            if (chat.text == ""):
                continue
            print(chat.text)

    def __search(self, query):
        self.browser.find_element(
            By.CLASS_NAME, "copyable-text").send_keys(query)
        return self.__wait("matched-text")

    def __openChat(self, q):
        # Get the first chat from search results
        self.__search(q).click()

    def __getChatName(self):
        return self.browser.find_element(By.CLASS_NAME, "_2rlF7").text

    def __scrollToTop(self, e):
        e[0].click()

    def __scrollToBottom(self, e):
        pass

# Scroll up waiting for DOM to not change anymore. Means we reached the top
# Incremental waits of 1 and 3 seconds are used to avoid false positives
    def __sendPageUP(self, count):
        for i in range(count):
            ActionChains(self.browser).send_keys(Keys.PAGE_UP).perform()
            time.sleep(0.1)

    def __scrollToView(self, e):
        ee = self.browser.find_elements(By.CLASS_NAME, e)
        ee[0].click()
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

    def getMessages(self, chatName, all=False):
        self.__openChat(chatName)
        self.__wait("_7GVCb")

        self.browser.find_elements(By.CLASS_NAME, "_7GVCb")[0].click()

        if all:
            self.__scrollToView("_7GVCb")

        time.sleep(3)
        messages = self.browser.find_elements(By.CLASS_NAME, "_7GVCb")

        fetchedMessages = []
        for message in messages:
            msg = self.__parseMessage(message)
            fetchedMessages.append(msg)
            print(msg)
            print("------------------")

        self.__saveToCSV(fetchedMessages, self.__getChatName())

    def getMessagesOutgoing(self, chatName, all=False):
        self.__openChat(chatName)
        self.__wait("message-out")

        if all:
            self.__scrollToView("message-out")

        time.sleep(3)
        messages = self.browser.find_elements(By.CLASS_NAME, "message-out")

        fetchedMessages = []
        for message in messages:
            msg = self.__parseMessage(message)
            fetchedMessages.append(msg)
            print(msg)
            print("------------------")

        self.__saveToCSV(fetchedMessages, self.__getChatName())

    def getMessagesIncomming(self, chatName, all=False):
        self.__openChat(chatName)
        self.__wait("message-in")

        if all:
            self.__scrollToView("message-in")

        time.sleep(3)
        messages = self.browser.find_elements(By.CLASS_NAME, "message-in")

        fetchedMessages = []
        for message in messages:
            msg = self.__parseMessage(message)
            fetchedMessages.append(msg)
            print(msg)
            print("------------------")

        self.__saveToCSV(fetchedMessages, self.__getChatName())

    def __parseMessage(self, message):
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
                    By.CLASS_NAME, "_3FuDI._11JPr")[-1].text  # Any Reply to Other Person
                # Check if you exists somehwere
                for z in message.find_elements(By.CLASS_NAME, "_11JPr"):
                    if "You" in z.text:
                        repliedTo = "You"
            except:  # Wildcard reply to me
                repliedTo = "You"  # Reply to me

        except:  # There is not a reply
            repliedTo = "NONE"
            repliedMsg = "NONE"

        date = message.find_elements(
            By.CLASS_NAME, "l7jjieqr.fewfhwl7")[-1].text

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
                data_plain_t = message.find_elements(
                    By.CLASS_NAME, "copyable-text")[0].get_attribute('data-pre-plain-text')
                msgSender = data_plain_t[data_plain_t.find(
                    "] ")+2:-1]  # Parse name from data

        # Different wordarounds | Should be solved
        if msg == "":
            msg = "Emoji"
        if repliedMsg == "":
            repliedMsg = "Emoji"
        if len(repliedMsg) == 4 and repliedMsg[1] == ":":
            repliedMsg = "VOICE NOTE"
        return (date, msgSender, msg, repliedTo, repliedMsg)

    def __isLogin(self):
        try:
            # Landing Page (Login QR Code page)
            self.browser.find_element(By.CLASS_NAME, "landing-wrapper")
        except:
            try:
                # Logged in (Chat list)
                self.browser.find_element(By.CLASS_NAME, "two")
                return True
            except:
                time.sleep(3)
                self.__isLogin()
        return False

    def __wait(self, cName, timeout=60):
        print("Waiting for element: {}".format(cName),
              " To load, timeout: {}".format(timeout), " seconds remaining")
        wait = WebDriverWait(self.browser, timeout)
        try:
            element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, cName)))
        except:
            exit("Element not found")
        return element

    def __saveToCSV(self, data, name):
        fileName = name + ".csv"
        with open(fileName, 'w', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(("Date", "Sender", "Message",
                            "Replied To", "Replied Message"))
            writer.writerows(data)
            # for item in data:
            #     writer.writerows(item[0], item[1], item[2], item[3])


bot = WhatsExtract(silent=True, headless=False)
bot.login()
bot.getMessages("Bawa", all=False)
