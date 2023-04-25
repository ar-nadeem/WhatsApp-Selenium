# WhatsApp-Selenium

## What is this

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Google Chrome](https://img.shields.io/badge/Google%20Chrome-4285F4?style=for-the-badge&logo=GoogleChrome&logoColor=white)

This is fully automated version of Whatsapp on Selenium. Cause Meta wants you to pay for their own.

This is a selenium based python framework, that will allow you extract or send messages from whatsapp, which will be saved in a .CSV file. You can later run data analysis on it or train a model.

The App uses Web.Whatsapp.com to extract messages in an automated fashion. You will be provided with a QR-Code on first run to login. After that you can start extracting in Headless mode. Browser Data/Session is saved in UserData folder in same directory as your script.

# How to use ?

### Setup

1. First clone the prjoect then install requirements from the `requirements.txt`

```bash
pip install -r requirements.txt
```

2. Install **_Chrome web driver_** from here https://chromedriver.chromium.org/downloads and **_Chrome browser_** from here https://www.google.com/chrome. Make sure to add your web driver to your system path, although it is not necessary.

3. You can import the `WhatsExtract.py` into your main python file.

```python
from Whatsapp import Whatsapp
```

### Usage

Now you can use the object of the class to extract message.
Example 1:

```python
bot = Whatsapp(silent=True, headless=False)
bot.login()
bot.getMessages("Alex", scroll=10)
```

### Options

#### Default Constructor

For the default constructor you have three options

1. `executable_path` You can specifiy the path from your Chrome driver if not already in your system PATH. The Format should be like `C:/Driver/chromedriver.exe`.
2. `silent` has two options `True` or `False`. If set to True, it will not display selenium logs.
3. `headless` has two options `True` or `False`. If set to True, the browser will be headless (not visible).

#### Function getMessages

Has 4 arguments

1. `chatName` - This will be the chatname you want to extract messages from. Could be part of the chatName. It utilizes WhatsApp chat search to find the chat.
2. `all` has two options `True` or `False`. If set to True, will true to extract all available chats. Although it may stop before that, see **_OPTION 4_**.
3. `scroll` You can set to any integer for scolling some of the chat, to extract more messages.
4. `manualSync` has two options `True` or `False`. If set to True, script will wait for your input before it start extracting messages. Its so can manually scroll to where you want the messages extraction to begin from.

#### Function replyTo

Has 2 arguments

1. `element` - This is message element, you want to reply to. It is a selenium object
2. `msg` Its the message you want to send.

#### Function hookIncomming

Has 2 arguments. Return last incomming message element and parsed message.

1. `chatName` - This is chat name you want to listen to.
2. `func` This is a async function you set to do things with the message returned.

Example:

```python
responses = {"hello": "Hello, Nice to meet you !", "How are you ?": "I'm fine, thank you !",
                "Who are you ?": "My name is RevBot, I'm a chatbot made by AbdulRahman Nadeem."}

async def func(element, msg):
    print(msg)
    if (msg[2] == "EXIT!"):
        bot.browser.close()
        exit()

    if (msg[2].lower() == "help"):
        bot.replyTo(
            element, str("My commands are : " + str(responses)))
    else:
        try:
            bot.replyTo(element, responses[msg[2].lower()])
        except:
            bot.replyTo(element, "I don't understand !")

bot.hookIncomming("AbdulRahman", func)

```

## BUGS

- Sometimes the sender name will be mangled.
- Unable to diffrentiate between VoiceNote in a replied message.
- Too many workarounds done in script, which might fail.

## Features to be added

- Add support for Emojis
- Add support to diffrentiate between different media.
- Better Sync controll, to download all messages.
