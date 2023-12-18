from bs4 import BeautifulSoup
import requests
import validators
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sys import exit
from fake_useragent import UserAgent
from itertools import groupby

INTEGRATED_HEADERS = {
    "User-Agent": UserAgent().random
}


def gather_mails(url):
    mail_list = []
    possible_tags = [
        "a", "h1", "h2", "h3", "h4", "h5", "h6", "b", "em", "i", "code", "kbd", "pre", "abbr", "bdo", "blockquote", "q",
        "cite", "p", "td"]
    try:
        request = requests.get(url, headers=INTEGRATED_HEADERS).text
        soup = BeautifulSoup(request, "html.parser")
        for tag in possible_tags:
            mails = soup.findAll(tag)
            for mail in mails:
                if validators.email(mail.text):
                    mail_list.append(mail.text)

        mail_list = [el for el, _ in groupby(mail_list)]
        return mail_list
    except:
        return []


def get_urls(_url):
    try:
        req = requests.get(_url, headers=INTEGRATED_HEADERS).text
        soup = BeautifulSoup(req, 'html.parser')
        urls = soup.findAll('a')
        url_list = []
        conn_type = 'https' if _url[:5] == 'https' else 'http'
        site = _url.split(f'{conn_type}://')[1].rstrip('/')

        for url in urls:
            if url["href"][0] != '/':
                if url["href"][:4] == 'http':
                    url_list.append(url["href"])
            else:
                url_list.append(f'{conn_type}://{site}{url["href"]}')
        return url_list
    except:
        return []


def send_email(sender, password, recipient, subject, text):
    msg = MIMEMultipart('alternative')
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    txt = MIMEText(text, 'plain')
    msg.attach(txt)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender, password)
    except:
        print("Could not log in with the provided email and password")
        exit(-1)

    try:
        server.sendmail(sender, recipient, msg.as_string())
        print(f'[Sent]!')
    except:
        print(f'Error sending message to {recipient}')


# Menu
print("ToolDox Panel \n")

URL_TO_SEND = input("Enter URL to parse all mails: ")
if not validators.url(URL_TO_SEND):
    print("Invalid URL")
    exit(-1)

print("Gathering mails...")
all_mails = gather_mails(URL_TO_SEND) + [mail for url in get_urls(URL_TO_SEND) for mail in gather_mails(url)]

if len(all_mails) == 0:
    print(f'Mails were not found.')
    exit(-1)

print("Emails:", ', '.join(all_mails))
print(f"\nTotal emails gathered: {len(all_mails)}")

input('Press enter to continue')

print(f'Your Data:\n')
email = input('Enter your email email: ')
password = input("Enter email's password: ")
subject = input('Enter subject of your message: ')
text = input('Enter text to send: ')

for recipient in all_mails:
    send_email(email, password, recipient, subject, text)
