import re
from Whatsapp.Whatsapp import Whatsapp
import random
import asyncio


jbh = ["Ach.", "Ok sir.", "JBH +1"]

bawa = ["Is someone talking about bawa ? Bawa is king !"]


bott = ["Hi from bot"]

# ,executable_path="/var/lib/flatpak/exports/bin/org.chromium.Chromium")
bot = Whatsapp(silent=True, headless=False)


async def func(element, msg):

    if (re.search(r"^jbh$|^jbh\.$", msg[2].lower())):
        print(msg)
        bot.replyTo(element, jbh[random.randrange(len(jbh))])

    if (re.search(r"^.*bawa.*$", msg[2].lower())):
        print(msg)
        bot.replyTo(element, bawa[random.randrange(len(bawa))])

    if (re.search(r"^.*bot.*$", msg[2].lower())):
        print(msg)
        bot.replyTo(element, bott[random.randrange(len(bott))])


bot.login()

# print("Reading messages now !")
bot.getChats()
# bot.hookIncomming("Fatima ", func)
