from vonage import Vonage, Auth

auth = Auth(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET')
vonage = Vonage(auth)
sms = vonage.sms

responseData = sms.send_message(
    {
        "from": "Vonage APIs",
        "to": "YOUR_PHONE_NUMBER",
        "text": "a text from vonage as a test!"
    }
)

if responseData['messages'][0]['status'] == '0':
    print("Message sent successfully.")
else:
    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
