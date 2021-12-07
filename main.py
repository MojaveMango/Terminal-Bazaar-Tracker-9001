import requests
import json
import pandas as pd
import time
import os


class Item:
    def __init__(self, name, topBuyOffer, topSellOffer, sellVolume, buyVolume, sellVolWeek, buyVolWeek):
        # explicit data
        self.name = name
        self.topBuyOffer = topBuyOffer
        self.topSellOffer = topSellOffer
        self.sellVolume = sellVolume
        self.buyVolume = buyVolume
        self.buyVolWeek = buyVolWeek
        self.sellVolWeek = sellVolWeek
        # implicit data. Don't make fun of me I don't want to learn real exception handling :(
        try:
            self.backlog = round(buyVolume / (buyVolWeek / 7), 2)
            pass
        except(TypeError, ZeroDivisionError):
            self.backlog = 0
            pass
        self.flatMargin = round(topSellOffer - topBuyOffer, 2)
        try:
            self.percentMargin = 100 * round((topSellOffer - topBuyOffer) / topBuyOffer, 3)
            pass
        except(TypeError, ZeroDivisionError):
            self.percentMargin = 0
            pass
        try:
            if (buyVolume / sellVolume) >= 1:
                self.salesRatio = round((buyVolume / sellVolume), 2)
            else:
                self.salesRatio = round(-1 / (buyVolume / sellVolume), 2)
            pass
        except(TypeError, ZeroDivisionError):
            self.salesRatio = 0
            pass
        self.time = int(time.time())


def clear(): os.system('cls')


def getAPI():
    # Loads Bazaar data from the hypixel API
    response_API = requests.get('https://api.hypixel.net/skyblock/bazaar?key=07a447d1-f4ff-4012-90df-4b58fd54dc7e')
    data = response_API.text
    parseJSON = json.loads(data)
    # Weird unexplained and non-existent items given by the API. Not the real Carrot on a stick or booster cookie.
    parseJSON['products'].pop('ENCHANTED_CARROT_ON_A_STICK')
    parseJSON['products'].pop('BAZAAR_COOKIE')
    return parseJSON


def writeItem(item):
    topBuyOffer = ''
    topSellOffer = ''

    name = item
    try:
        topBuyOffer = parse_json['products'][item]['sell_summary'][0]['pricePerUnit']
        pass
    except(TypeError, IndexError):
        print('No buy offers for', name)
        pass
    try:
        topSellOffer = parse_json['products'][item]['buy_summary'][0]['pricePerUnit']
        pass
    except(TypeError, IndexError):
        print('No sell offers for', name)
        pass
    buyVolume = parse_json['products'][item]['quick_status']['sellVolume']
    sellVolume = parse_json['products'][item]['quick_status']['buyVolume']
    buyVolWeek = parse_json['products'][item]['quick_status']['sellMovingWeek']
    sellVolWeek = parse_json['products'][item]['quick_status']['buyMovingWeek']
    writtenItem = Item(name, topBuyOffer, topSellOffer, sellVolume, buyVolume, sellVolWeek, buyVolWeek)
    return writtenItem


# Probably a better way to do this. Adds an item to the dataframe
def writeToHistory(item):
    # df1 = pd.read_csv('history/history.csv')
    df1 = pd.read_csv('history/' + item.name.replace(':', '') + '.csv')
    df2 = {
        'UNIX Time': item.time,
        'ID': item.name,
        'Top Buy Offer': item.topBuyOffer,
        'Top Sell Offer': item.topSellOffer,
        'Sell Volume': item.sellVolume,
        'Buy Volume': item.buyVolume,
        'Sell Volume Week': item.sellVolWeek,
        'Buy Volume Week': item.buyVolWeek,
        'Backlog': item.backlog,
        'Flat Margin': item.flatMargin,
        'Percent Margin': item.percentMargin,
        'Sales Ratio': item.salesRatio
    }
    df1 = df1.append(df2, ignore_index=True)
    print(item.name)
    return df1


def flatMarginSort(money):
    return money.flatMargin


def percentMarginSort(money):
    return money.percentMargin


def buyVolumeSort(money):
    return money.buyVolume


def sellVolumeSort(money):
    return money.sellVolume


# Stolen straight from https://github.com/ianrenton/Skyblock-Bazaar-Flipping-Calculator. Higher backlogs = higher
# chance you'll be stuck with the items longer before you can sell them.
def backlogSort(money):
    return money.backlog


# The number of buy offers compared to the number of sell offers. Negatives are faster to fill buy orders,
# positives are faster to fill sell orders. It is normally much slower to buy than it is to sell
def salesRatioSort(money):
    return money.salesRatio


if __name__ == '__main__':
    pd.set_option("display.max_columns", None)
    parse_json = getAPI()
    liveListOfItems = [writeItem(x) for x in parse_json['products'].keys()]

    sortBy = buyVolumeSort
    liveListOfItems.sort(reverse=True, key=sortBy)

    while True:
        # print(df.loc[df['UNIX Time'] == 1638893340])
        parse_json = getAPI()
        liveListOfItems = [writeItem(x) for x in parse_json['products'].keys()]
        for x in liveListOfItems:
            df = writeToHistory(x)
            df.to_csv('history/' + x.name + '.csv', index=False)
        clear()
        # flatMarginSort, percentMarginSort, buyVolumeSort, sellVolumeSort, salesRatioSort, backlogSort
        print('Item', '|', sortBy.__name__)
        for x in liveListOfItems:
            print(x.name, ':', sortBy(x))
        time.sleep(5)
