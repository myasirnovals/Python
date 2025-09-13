import os
import math
import random
import smtplib

digits = '0123456789'
OTP = ''

for i in range(6):
    OTP += digits[math.floor(random.random() * 10)]

otp = OTP + ' is your OTP'
msg = otp

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('', 'password')

email_id = input('Enter your email id: ')

server.sendmail('', email_id, msg)
otp_message = input('Enter the OTP you received: ')

if otp_message == OTP:
    print('OTP verified')
else:
    print('please check your OTP again!')
