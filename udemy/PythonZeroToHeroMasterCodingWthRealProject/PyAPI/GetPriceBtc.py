# https://api.coinbase.com/v2/prices/buy?currency=USD

import requests


def inform_price(price):
    print("Hello there the price of BTC is good now. and the price is: ", price)

my_good_price = 211162.01
response = requests.get("https://api.coinbase.com/v2/prices/buy?currency=USD")
current_price = float(response.json()['data']['amount'])
if current_price < my_good_price:
    inform_price(current_price)
