import psutil
import smtplib

from email.mime.text import MIMEText

sender_email = ''
receiver_email = ''
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = ''
smtp_password = ''


def send_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print('Alert email sent! successfully!')
    except Exception as e:
        print(f'Failed to send email alert: {e}')


def monitor_system():
    try:
        cpu_treshold = 80
        memory_treshold = 80

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        if cpu_usage > cpu_treshold:
            send_alert('High CPU usage', f'CPU usage is {cpu_usage}%')

        if memory_usage > memory_treshold:
            send_alert('High memory usage', f'Memory usage is {memory_usage}%')
    except  Exception as e:
        print(f'An error occurred while monitoring: {e}')


monitor_system()
