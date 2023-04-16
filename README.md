# WhatsAppExtractor

## What is this

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Google Chrome](https://img.shields.io/badge/Google%20Chrome-4285F4?style=for-the-badge&logo=GoogleChrome&logoColor=white)

This is a selenium based python framework, that will allow you extract messages from whatsapp, which will be saved in a .CSV file. You can later run data analysis on it or train a model.

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
from WhatsExtract import WhatsExtract
```

### Usage

Now you can use the object of the class to extract message.
Example 1:

```python
bot = WhatsExtract(silent=True, headless=False)
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

## BUGS

- Sometimes the sender name will be mangled.
- Unable to diffrentiate between VoiceNote in a replied message.
- Too many workarounds done in script, which might fail.

## Features to be added

- Add support for Emojis
- Add support to diffrentiate between different media.
- Better Sync controll, to download all messages.
