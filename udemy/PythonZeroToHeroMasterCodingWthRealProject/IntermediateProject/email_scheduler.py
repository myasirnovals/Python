import smtplib
import schedule
import time

def send_email():
    sender_email = ''
    receiver_email = ''
    password = ''

    subject = 'Hello from Python'
    body = 'This is a test email sent from Python! 3'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, receiver_email, message)
        print('Email sent successfully!')

schedule.every(1).minutes.do(send_email)

while True:
    schedule.run_pending()
    time.sleep(1)