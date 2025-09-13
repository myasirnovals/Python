import csv, smtplib, ssl
from datetime import date


def send_email(from_address, password, to_address, message):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(from_address, password)
        server.sendmail(from_address, to_address, message)


def main():
    today = date.today().strftime('%B %d %Y')
    message = ''' Subject: Your evaluation hi {name}, the date of your Q1 evaluation is {date} your score is {score}'''
    from_address = ''
    password = ''

    with open('student.csv') as file:
        reader = csv.reader(file)
        for name, email, score in reader:
            send_email(from_address, password, email, message.format(name=name, date=today, score=score))

            if send_email:
                print('email send for ' + name)
            else:
                print('email not send for ' + name)


if __name__ == '__main__':
    main()
