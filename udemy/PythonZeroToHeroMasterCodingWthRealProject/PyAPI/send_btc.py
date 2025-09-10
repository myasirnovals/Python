from vonage import Vonage, Auth

import sys
import requests

auth = Auth(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')
vonage = Vonage(auth)
sms = vonage.sms


def inform_price(price):
    responseData = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": "YOUR_PHONE_NUMBER",
            "text": "Hello there, Now the price of BTC is good and it is: %f" % price
        }
    )

    if responseData['messages'][0]['status'] == '0':
        print("Message sent successfully.")
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")


my_good_price = 211162.01

try:
    response = requests.get("https://api.coinbase.com/v2/prices/buy?currency=USD")
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from Coinbase: {e}")
    sys.exit(1)

current_price = float(response.json()['data']['amount'])
print(f"Current BTC Price: ${current_price}")

if current_price < my_good_price:
    print("Price is good, sending SMS...")
    inform_price(current_price)
else:
    print("Price is not in the desired range.")
