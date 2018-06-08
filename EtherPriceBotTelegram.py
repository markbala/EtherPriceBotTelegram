# Written by Mark Balakrishnan
# Telegram Cryptocurrency Price BOT based on Gareth Dwyer's "Building a Telegram Bot Using Telegram and Python Tutorial"

#Enter your BOT's TOKEN before use, and proxy settings if necessary
#Run script, then type a message "/ether" in a Telegram chat with your BOT

import json, requests, time, urllib, sqlite3, os

#TOKEN = "<enter TOKEN which is issued by BOTFather and uncomment this line. Do not delete inverted commas.>"

proxies = None #default is None
#proxies = {'https': 'https://<address>:<port>', 'http':'http://<address>:<port>'}  #uncomment if you need this to work behind a proxy

class TelegramBot(object):

    def __init__(self,TOKEN):
        self.TOKEN = TOKEN
        self.URL = "https://api.telegram.org/bot{}/".format(TOKEN)
        self.url1 = 'https://api.korbit.co.kr/v1/ticker?currency_pair=eth_krw'
        if proxies:
            print('using proxy')
        else:
            print('no proxy')

    def _getUrl(self,url):
        if proxies:
            response = requests.get(url, proxies=proxies,timeout=100)
        else:
            response = requests.get(url, timeout=100)
        content = response.content.decode("utf8")
        return content

    def _getJsonFromURL(self,url):
        content = self._getUrl(url)
        js = json.loads(content)
        return js

    def _getUpdates(self, offset=None):
        url = self.URL+"getUpdates?timeout=60"
        if offset:
            url += "&offset={}".format(offset)
        js = self._getJsonFromURL(url)
        return js

    def getLastUpdateId(self,updates):
        updates_ids = []
        for update in updates['result']:
            updates_ids.append(int(update["update_id"]))
        return max(updates_ids)

    def getLastChatIdAndText(self, updates):
        numUpdates = len(updates['result'])
        lastUpdate = numUpdates -1
        text = updates["result"][lastUpdate]["message"]["text"]
        chatId = updates["result"][lastUpdate]["message"]["chat"]["id"]
        return (text, chatId)

    def sendMessage(self,text, chatId):
        text = urllib.parse.quote_plus(text)
        url = self.URL+"sendMessage?text={}&chat_id={}".format(text,chatId)
        self._getUrl(url)

    def main(self):
        self.lastUpdateId = None
        while True:
            self.updates = self._getUpdates(self.lastUpdateId)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+":"+str(self.updates))
            if len(self.updates["result"]) > 0:
                self.lastUpdateId = self.getLastUpdateId(self.updates) + 1
                self.executionFunction(self.updates)

    def executionFunction(self,updates):
        for update in updates["result"]:
            try:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                if text == "/ether":
                    ethkrw = self._getJsonFromURL('https://api.korbit.co.kr/v1/ticker?currency_pair=eth_krw')
                    ethsgd = self._getJsonFromURL('https://coinhako.com/api/v1/price/currency/ETHSGD')
                    ethsgd = ethsgd['data']['buy_price']
                    message1 = "Buy ETH on Coinhako S$ at "+str(ethsgd)
                    ETHspread = (float(ethkrw["last"])/802.43 - float(ethsgd))/float(ethsgd)
                    ETHspreadPercentage = "{0:.2f}%".format(ETHspread*100)
                    message2 = str(ETHspreadPercentage)+" spread to Korbit, which trades at "+str("{0:.2f}".format(float(ethkrw["last"])/816.94))
                    print(message1+"\n"+message2)
                    self.sendMessage(message1+"\n"+message2,chat)
                elif text == '/help':
                    self.sendMessage("Welcome to Mark's Ether Price Tracking BOT\n\'/ether' to retrieve current ETH prices on CoinHako and Korbit."", chat)
                elif text == '/start':
                    self.sendMessage("Hi there, {}! Welcome to Mark's Ether Price Tracking BOT.\nType '/ether' to retrieve current ETH prices on CoinHako and Korbit. Full code available at https://github.com/markbala/EtherPriceBotTelegram".format(update["message"]["from"]["first_name"]),chat)
            except:
                pass

while True:
    try:
        print('BOT Started')
        TelegramBOT = TelegramBot(TOKEN)
        TelegramBOT.main()
    except Exception as e:
        print(e)
        del TelegramBOT
        time.sleep(5)
        print('Restarting in 5 seconds. Error at: '+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
